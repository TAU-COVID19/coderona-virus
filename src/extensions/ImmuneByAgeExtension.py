from src.seir import DiseaseState
from src.simulation.simulation import Simulation
from src.world import world
from src.world.environments import InitialGroup

class ImmuneByAgeExtension(Simulation):
    def __init__(self):
        self.ImmunePortion = 0.1
        self.MinAgeToImmune = -1
        self.MaxAgeToImmune = 11
        print("In ImmuneByAgeExtension")

    def DoProcessing(self):
        """
        if portion of population that is immune > self.ImmunePortion Do nothing
        else immune by age group
        """
        cnt  = sum([1 for p in self._world.all_people() if( p.get_disease_state() != DiseaseState.IMMUNE) and (( p.get_disease_state() != DiseaseState.DECEASED))])
        num_people  = sum([1 for p in self._world.all_people() if p.get_disease_state() != DiseaseState.DECEASED])
        potionUntilNow = cnt / num_people
        if self.ImmunePortion > potionUntilNow:
            peopleToImmune = [p for p in self.world.all_people() if  (self.MinAgeToImmune < p.get_age_category()) and (p.get_age_category() < self.MaxAgeToImmune)]
            for person in peopleToImmune:
                self.register_events(person.immune_and_get_events(self._date, InitialGroup.initial_group()))
        self.MinAgeToImmune = self.MinAgeToImmune + 10
        self.MinAgeToImmune = self.MaxAgeToImmune + 10
        print("")
