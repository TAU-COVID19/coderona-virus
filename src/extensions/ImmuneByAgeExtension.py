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


class ImmuneByAgeExtension(Simulation):
    def __init__(self, parent: Simulation):
        # change the following parameters to affect the vaccination flow
        self.target_immune_percentage = 0.5
        self.min_age_to_immune = 18
        self.max_age_to_immune = 100
        self.max_people_to_immune_a_day = 5000
        self.immune_strategy = ImmuneStrategy.ANY_AGE

        # internal state. do not change!
        self.parent = parent
        if self.immune_strategy == ImmuneStrategy.OLDER_TO_YOUNGER:
            self.state_max_age_to_immune = self.max_age_to_immune
            self.state_min_age_to_immune = self.max_age_to_immune - 10
        elif self.immune_strategy == ImmuneStrategy.YOUNGER_TO_OLDER:
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

        if self.target_immune_percentage > immuned_percentage:
            people_to_immune = [p for p in self.parent._world.all_people()
                                if (self.can_immune(p.get_disease_state())) and
                                (p.get_age_category() > self.state_min_age_to_immune) and
                                (p.get_age_category() < self.state_max_age_to_immune)]
            print(f"ImmuneByAgeExtension({self.immune_strategy}): found today {len(people_to_immune)} people " +
                  f"between {self.state_min_age_to_immune} to {self.state_max_age_to_immune}")
            seq(people_to_immune).take(self.max_people_to_immune_a_day).for_each(
                lambda person: self.parent.register_events(
                    person.immune_and_get_events(start_date=self.parent._date, delta_time=timedelta(0))))

            # advance to the next age group only if you covered the current age group
            if len(people_to_immune) <= self.max_people_to_immune_a_day:
                if self.immune_strategy == ImmuneStrategy.OLDER_TO_YOUNGER:
                    self.state_min_age_to_immune = max(self.state_min_age_to_immune-10, self.min_age_to_immune)
                elif self.immune_strategy == ImmuneStrategy.YOUNGER_TO_OLDER:
                    self.state_max_age_to_immune = min(self.state_max_age_to_immune+10, self.max_age_to_immune)
                elif self.immune_strategy == ImmuneStrategy.ANY_AGE:
                    pass # do nothing
                else:
                    assert False, "immune_strategy is Out Of Range!"

