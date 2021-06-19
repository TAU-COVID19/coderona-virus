from datetime import timedelta
from src.seir import DiseaseState
from src.simulation.simulation import Simulation
from src.world import world
from src.world.environments import InitialGroup
from functional import seq


class ImmuneByAgeExtension(Simulation):
    def __init__(self, parent: Simulation):
        self.ImmunePortion = 0.5
        self.MinAgeToImmune = 18
        self.MaxAgeToImmune = 99
        self.AgeGroupYears = 10
        self.MaxVaccinationsADay = 1000
        self.parent = parent

    def start_of_day_processing(self):
        pass

    def end_of_day_processing(self):
        """
        Immune up to 1000 people a day, each time from older to younger, group years of 10 years every time
        when the group year is all immune, we move 10 years down the group year
        """

        """
        if portion of population that is immune > self.ImmunePortion Do nothing
        else immune by age group
        """
        number_of_immune_people = seq(self.parent._world.all_people()).count(
            lambda p: ((p.get_disease_state() == DiseaseState.IMMUNE) and
                       (p.get_disease_state() != DiseaseState.DECEASED)))
        # tmp = [1 for p in self.parent._world.all_people() if
        #        ((p.get_disease_state() == DiseaseState.IMMUNE) and (p.get_disease_state() != DiseaseState.DECEASED))]
        # number_of_immune_people = sum(tmp)
        total_number_of_not_dead = sum(
            [1 for p in self.parent._world.all_people() if p.get_disease_state() != DiseaseState.DECEASED])
        portion_of_immune_people = number_of_immune_people / total_number_of_not_dead
        people_to_immune = seq([])
        min_year_to_immune = max(self.MaxAgeToImmune - self.AgeGroupYears, self.MinAgeToImmune)
        if self.ImmunePortion > portion_of_immune_people and self.MaxAgeToImmune > self.MinAgeToImmune:
            people_to_immune = seq([p for p in self.parent._world.all_people() if
                                    (p.get_age_category() >= min_year_to_immune) and
                                    (p.get_age_category() <= self.MaxAgeToImmune) and
                                    ((p.get_disease_state() == DiseaseState.SUSCEPTIBLE) or
                                     (p.get_disease_state() == DiseaseState.LATENT))]
                                   ).take(self.MaxVaccinationsADay)
        print(f"IMMUNE: from {min_year_to_immune} to {self.MaxAgeToImmune}, {people_to_immune.len()} people ")
        if people_to_immune.len() == 0 and self.MaxAgeToImmune >= self.MinAgeToImmune:
            self.MaxAgeToImmune = self.MaxAgeToImmune - self.AgeGroupYears
        for person in people_to_immune.list():
            self.parent.register_events(
                person.immune_and_get_events(self.parent._date + timedelta(1), InitialGroup.initial_group()))
        print("")
