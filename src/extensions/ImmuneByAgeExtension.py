from datetime import timedelta
from src.seir import DiseaseState
from src.simulation.simulation import Simulation
from src.world import world
from src.world.environments import InitialGroup
from functional import seq


class ImmuneStrategy:
    YOUNGER_TO_OLDER = 1
    OLDER_TO_YOUNGER = 2
    ANY_AGE = 3

    def __init__(self, order: int, immune_by_households: bool, immune_everybody_in_the_house: bool):
        """
        if self.immune_by_households then if immune_everybody_in_the_house is True as well,
        then if vaccinating one person at home, we will vaccinate ALL the household
        """
        self.order = order
        self.immune_by_households = immune_by_households
        self.immune_everybody_in_the_house = immune_everybody_in_the_house

    def get_order(self):
        return self.order

    def is_by_households(self):
        return self.immune_by_households

    def is_immune_everybody_in_the_house(self):
        return self.immune_everybody_in_the_house

    def __str__(self):
        by_household = "Random"
        if self.immune_by_households:
            if self.immune_everybody_in_the_house:
                by_household = "By Household, All or nothing"
            else:
                by_household = "By Household"
        if self.order == self.YOUNGER_TO_OLDER:
            return "YOUNGER_TO_OLDER" + ", " + by_household
        elif self.order == self.OLDER_TO_YOUNGER:
            return "OLDER_TO_YOUNGER" + ", " + by_household
        else:
            return "ANY_AGE" + ", " + by_household


class ImmuneByAgeExtension(Simulation):
    def __init__(self, parent: Simulation):
        # change the following parameters to affect the vaccination flow
        self.target_immune_percentage = 0.8
        self.min_age_to_immune = 18
        self.max_age_to_immune = 100
        self.max_people_to_immune_a_day = 800
        self.immune_strategy: ImmuneStrategy = ImmuneStrategy(
            order=ImmuneStrategy.ANY_AGE,
            immune_by_households=True,
            immune_everybody_in_the_house=False)

        # internal state. do not change!
        self.parent = parent
        if self.immune_strategy.get_order() == ImmuneStrategy.OLDER_TO_YOUNGER:
            self.state_max_age_to_immune = self.max_age_to_immune
            self.state_min_age_to_immune = self.max_age_to_immune - 10
        elif self.immune_strategy.get_order() == ImmuneStrategy.YOUNGER_TO_OLDER:
            self.state_min_age_to_immune = self.min_age_to_immune
            self.state_max_age_to_immune = self.min_age_to_immune + 10
        else:
            self.state_min_age_to_immune = self.min_age_to_immune
            self.state_max_age_to_immune = self.max_age_to_immune

    def can_immune(self, state: DiseaseState) -> bool:
        if state in (DiseaseState.INCUBATINGPOSTLATENT, DiseaseState.ASYMPTOMATICINFECTIOUS, DiseaseState.LATENT,
                     DiseaseState.SUSCEPTIBLE):
            return True
        else:
            return False

    def end_of_day_processing(self):
        pass

    def start_of_day_processing(self):
        """
        if portion of population that is immune > self.ImmunePortion Do nothing
        else immune by the selected ImmuneStrategy
        """
        immuned = seq(self.parent._world.all_people()).count(lambda p: p.get_disease_state() == DiseaseState.IMMUNE)
        not_deceased = seq(self.parent._world.all_people()).count(
            lambda p: p.get_disease_state() != DiseaseState.DECEASED)
        immuned_percentage = immuned / not_deceased

        people_to_immune = []
        if self.target_immune_percentage > immuned_percentage:
            if self.immune_strategy.is_by_households():
                households = [h for h in self.parent._world.get_all_city_households()]
                for h in households:
                    people_to_immune = []
                    if self.immune_strategy.is_immune_everybody_in_the_house():
                        # if one person can be vaccinated in this household, vaccinate ALL the eligible people
                        if seq(h.get_people()).count(
                                lambda p: self.can_immune(p.get_disease_state()) and
                                          (p.get_age_category() > self.state_min_age_to_immune) and
                                          (p.get_age_category() < self.state_max_age_to_immune)) > 0:
                            people_to_immune += [p for p in h.get_people()
                                                 if (self.can_immune(p.get_disease_state())) and
                                                 (p.get_age_category() >= 18) and
                                                 (p.get_age_category() < self.state_max_age_to_immune)]
                    else:
                        people_to_immune += [p for p in h.get_people()
                                             if (self.can_immune(p.get_disease_state())) and
                                             (p.get_age_category() > self.state_min_age_to_immune) and
                                             (p.get_age_category() < self.state_max_age_to_immune)]
                    if len(people_to_immune) > self.max_people_to_immune_a_day:
                        break
            else:
                people_to_immune = [p for p in self.parent._world.all_people()
                                    if (self.can_immune(p.get_disease_state())) and
                                    (p.get_age_category() > self.state_min_age_to_immune) and
                                    (p.get_age_category() < self.state_max_age_to_immune)]
            print(f"ImmuneByAgeExtension({str(self.immune_strategy)} " +
                  f"between {self.state_min_age_to_immune} to {self.state_max_age_to_immune}")
            seq(people_to_immune).take(self.max_people_to_immune_a_day).for_each(
                lambda person: self.parent.register_events(
                    person.immune_and_get_events(start_date=self.parent._date, delta_time=timedelta(0))))

            # advance to the next age group only if you covered the current age group
            if len(people_to_immune) <= self.max_people_to_immune_a_day:
                if self.immune_strategy.get_order() == ImmuneStrategy.OLDER_TO_YOUNGER:
                    self.state_min_age_to_immune = max(self.state_min_age_to_immune - 10, self.min_age_to_immune)
                elif self.immune_strategy.get_order() == ImmuneStrategy.YOUNGER_TO_OLDER:
                    self.state_max_age_to_immune = min(self.state_max_age_to_immune + 10, self.max_age_to_immune)
                elif self.immune_strategy.get_order() == ImmuneStrategy.ANY_AGE:
                    pass  # do nothing
                else:
                    assert False, "immune_strategy is Out Of Range!"
