import random
from datetime import timedelta
from functional import seq
from src.seir import DiseaseState
from src.simulation.initial_infection_params import InitialImmuneType
from src.simulation.simulation import Simulation


class ImmuneStrategy:
    NONE: int = 0,
    ASCENDING: int = 1,
    DESCENDING: int = 2,

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
        if self.order == self.ASCENDING:
            return "ASCENDING" + ", " + by_household
        elif self.order == self.DESCENDING:
            return "DESCENDING" + ", " + by_household
        else:
            return "ANY_AGE" + ", " + by_household


class ImmuneByAgeExtension(Simulation):
    def __init__(self, parent: Simulation):
        # super().__init__(world, initial_date)
        extension_parameters = parent._extension_params["ImmuneByAgeExtension"]
        print(f"ImmuneByAgeExtension() extension_parameters {str(extension_parameters)}")
        # change the following parameters to affect the vaccination flow
        self.days_since_start = 0
        self.target_immune_percentage = extension_parameters.per_to_Immune
        self.min_age_to_immune = extension_parameters.min_age
        self.max_age_to_immune = 100
        self.max_people_to_immune_a_day = extension_parameters.people_per_day
        self.immune_strategy: ImmuneStrategy = ImmuneStrategy(
            order=extension_parameters.order.value,
            immune_by_households=extension_parameters.immune_source in
                                 [InitialImmuneType.HOUSEHOLDS, InitialImmuneType.HOUSEHOLDS_ALL_AT_ONCE],
            immune_everybody_in_the_house=extension_parameters.immune_source == InitialImmuneType.HOUSEHOLDS_ALL_AT_ONCE)

        # internal state. do not change!
        self.parent = parent
        if self.immune_strategy.get_order() == ImmuneStrategy.DESCENDING:
            self.state_max_age_to_immune = self.max_age_to_immune
            self.state_min_age_to_immune = self.max_age_to_immune - 10
        elif self.immune_strategy.get_order() == ImmuneStrategy.ASCENDING:
            self.state_min_age_to_immune = self.min_age_to_immune
            self.state_max_age_to_immune = self.min_age_to_immune + 10
        else:
            self.state_min_age_to_immune = self.min_age_to_immune
            self.state_max_age_to_immune = self.max_age_to_immune

    def __str__(self):
        return f"ImmuneByAgeExtension() immune_percentage={self.target_immune_percentage}\n" + \
               f"min_age={self.min_age_to_immune}, max_age={self.max_age_to_immune}\n" + \
               f"self.max_people_to_immune_a_day={self.max_people_to_immune_a_day}\n" + \
               f"strategy={str(self.immune_strategy)}"

    def can_immune(self, state: DiseaseState) -> bool:
        if state in (DiseaseState.INCUBATINGPOSTLATENT, DiseaseState.ASYMPTOMATICINFECTIOUS,
                     DiseaseState.SUSCEPTIBLE):
            return True
        else:
            return False

    def start_of_day_processing(self):

            pass

    def end_of_day_processing(self):
        """
        if portion of population that is immune > self.ImmunePortion Do nothing
        else immune by the selected ImmuneStrategy
        """
        self.days_since_start += 1
        immuned = seq(self.parent._world.all_people()).count(lambda p: p.get_disease_state() == DiseaseState.IMMUNE)
        can_be_immuned = seq(self.parent._world.all_people()).count(
            lambda p: self.can_immune(p.get_disease_state()) and
                      (p.get_age_category() >= self.min_age_to_immune) and
                      (p.get_age_category() <= self.max_age_to_immune))
        immuned_percentage = (immuned / can_be_immuned) if can_be_immuned > 0 else 1.0

        people_to_immune = []
        if self.target_immune_percentage > immuned_percentage:
            if self.immune_strategy.is_by_households():
                households = [h for h in self.parent._world.get_all_city_households()]
                for h in households:
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
            random.shuffle(people_to_immune)
            print(f"ImmuneByAgeExtension({str(self.immune_strategy)}, (day {self.days_since_start}), " +
                  f"age {self.state_min_age_to_immune}-{self.state_max_age_to_immune}, immune {self.max_people_to_immune_a_day} a day, " +
                  f"immune % = {immuned}/{can_be_immuned} = {immuned_percentage*100.0:.1f}")
            seq(people_to_immune).take(self.max_people_to_immune_a_day).for_each(
                lambda person: self.parent.register_events(
                    person.immune_and_get_events(start_date=self.parent._date, delta_time=timedelta(days=0))))

            # advance to the next age group only if you covered the current age group
            if len(people_to_immune) <= self.max_people_to_immune_a_day:
                if self.immune_strategy.get_order() == ImmuneStrategy.DESCENDING:
                    self.state_min_age_to_immune = max(self.state_min_age_to_immune - 10, self.min_age_to_immune)
                elif self.immune_strategy.get_order() == ImmuneStrategy.ASCENDING:
                    self.state_max_age_to_immune = min(self.state_max_age_to_immune + 10, self.max_age_to_immune)
                elif self.immune_strategy.get_order() == ImmuneStrategy.NONE:
                    pass  # do nothing
                else:
                    assert False, "immune_strategy is Out Of Range!"
