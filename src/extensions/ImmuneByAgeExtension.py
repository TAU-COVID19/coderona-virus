import math
import random
from datetime import timedelta
from functional import seq
from src.seir import DiseaseState
from src.simulation.initial_infection_params import InitialImmuneType
from src.simulation.simulation import Simulation
from src.world import Person
from src.world.environments.neighborhood import NeighborhoodCommunity


class ImmuneStrategy:
    NONE: int = 0,
    ASCENDING: int = 1,
    DESCENDING: int = 2,

    def __init__(self, order: int, immune_by_households: bool, immune_everybody_in_the_house: bool,
                 immune_by_neighborhood: bool):
        """
        if self.immune_by_households then if immune_everybody_in_the_house is True as well,
        then if vaccinating one person at home, we will vaccinate ALL the household
        """
        self.order = order
        self.immune_by_households = immune_by_households
        self.immune_everybody_in_the_house = immune_everybody_in_the_house
        self.immune_by_neighborhood = immune_by_neighborhood

    def get_order(self):
        return self.order

    def is_by_households(self):
        return self.immune_by_households

    def is_by_neighborhood(self):
        return self.immune_by_neighborhood

    def is_immune_everybody_in_the_house(self):
        return self.immune_everybody_in_the_house

    def __str__(self):
        by_household = "Random"
        if self.immune_by_neighborhood:
            by_household = "By Neighborhood"
        elif self.immune_by_households:
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
        self.finished = False
        extension_parameters = parent._extension_params["ImmuneByAgeExtension"]
        print(f"ImmuneByAgeExtension() extension_parameters {str(extension_parameters)}")
        # change the following parameters to affect the vaccination flow
        self.days_since_start = 0
        # self.target_immune_percentage = extension_parameters.per_to_Immune
        self.target_immune_percentage = [
            0,  # AGE 0-9
            0.7,  # AGE 10-19
            0.73,  # AGE 20-29
            0.79,  # AGE 30-39
            0.82,  # AGE 40-49
            0.86,  # AGE 50-59
            0.88,  # AGE 60-69
            0.94,  # AGE 70-79
            0.92,  # AGE 80-89
            0.91  # AGE 90-99
        ]
        self.min_age_to_immune = extension_parameters.min_age
        self.max_age_to_immune = 100
        self.max_people_to_immune_a_day = extension_parameters.people_per_day
        self.immune_strategy: ImmuneStrategy = ImmuneStrategy(
            order=extension_parameters.order.value,
            immune_by_households=extension_parameters.immune_source in
                                 [InitialImmuneType.HOUSEHOLDS, InitialImmuneType.HOUSEHOLDS_ALL_AT_ONCE],
            immune_everybody_in_the_house=extension_parameters.immune_source == InitialImmuneType.HOUSEHOLDS_ALL_AT_ONCE,
            immune_by_neighborhood=extension_parameters.immune_source == InitialImmuneType.BY_NEIGHBORHOOD)

        # internal state. do not change!
        self.parent = parent
        if self.immune_strategy.immune_by_neighborhood:
            self.state_min_age_to_immune = self.min_age_to_immune
            self.state_max_age_to_immune = self.max_age_to_immune
        else:
            if self.immune_strategy.get_order() == ImmuneStrategy.DESCENDING:
                self.state_max_age_to_immune = math.floor((self.max_age_to_immune + 5) / 10) * 10
                self.state_min_age_to_immune = self.state_max_age_to_immune - 10
            elif self.immune_strategy.get_order() == ImmuneStrategy.ASCENDING:
                self.state_min_age_to_immune = self.min_age_to_immune
                self.state_max_age_to_immune = math.floor((self.min_age_to_immune + 15) / 10) * 10
            else:
                self.state_min_age_to_immune = self.min_age_to_immune
                self.state_max_age_to_immune = self.max_age_to_immune

    def __str__(self):
        return f"ImmuneByAgeExtension() immune_percentage={self.target_immune_percentage}\n" + \
               f"min_age={self.min_age_to_immune}, max_age={self.max_age_to_immune}\n" + \
               f"self.max_people_to_immune_a_day={self.max_people_to_immune_a_day}\n" + \
               f"strategy={str(self.immune_strategy)}"

    def _register_events(self, person: Person):
        ok, events = person.immune_and_get_events(start_date=self.parent._date, delta_time=timedelta(days=0))
        if ok:
            self.parent.register_events(events)

    def can_immune(self, state: DiseaseState) -> bool:
        if state in (DiseaseState.INCUBATINGPOSTLATENT, DiseaseState.ASYMPTOMATICINFECTIOUS,
                     DiseaseState.SUSCEPTIBLE):
            return True
        else:
            return False

    def start_of_day_processing(self):
        pass

    def count_sick_people(self, people):
        c = seq(people).count(lambda p: p.get_disease_state() in [DiseaseState.SYMPTOMATICINFECTIOUS])
        return c

    def get_age_category(self, p: Person):
        return p.get_age_category()

    def end_of_day_processing(self):
        """
        if portion of population that is immune > self.ImmunePortion Do nothing
        else immune by the selected ImmuneStrategy
        """
        self.days_since_start += 1
        immuned = seq(self.parent._world.all_people()).count(
            lambda p: p.get_disease_state() == DiseaseState.IMMUNE and
                      (self.state_min_age_to_immune < p.get_age_category() <= self.state_max_age_to_immune)
        )
        can_be_immuned = seq(self.parent._world.all_people()).count(
            lambda p: (self.can_immune(p.get_disease_state()) or (p.get_disease_state() == DiseaseState.IMMUNE)) and
                      (self.state_min_age_to_immune < p.get_age_category() <= self.state_max_age_to_immune)
        )
        immuned_percentage = (immuned / can_be_immuned) if can_be_immuned > 0 else 1.0

        people_to_immune = []

        target_percentage_index = max(0, int(self.state_min_age_to_immune / 10))
        target_percentage_index = min(len(self.target_immune_percentage) - 1, target_percentage_index)
        target_percentage = self.target_immune_percentage[target_percentage_index]

        # print(f"Immune: self.state_min_age_to_immune={self.state_min_age_to_immune}, "
        #       f"target={target_percentage}, "
        #       f"immuned_percentage={immuned_percentage}")
        if not self.finished:
            if self.immune_strategy.is_by_neighborhood():
                neighborhoods = seq(self.parent._world.all_environments).filter(
                    lambda e: isinstance(e, NeighborhoodCommunity))
                sick_per_neighborhood = neighborhoods.map(lambda n: seq(n.get_people()).count(
                    lambda p: p.get_disease_state() in [DiseaseState.SYMPTOMATICINFECTIOUS]))
                index_of_max = sick_per_neighborhood.to_list().index(sick_per_neighborhood.max())

                print(f"Immune neighborhood {index_of_max}, sick_per_neighborhood={sick_per_neighborhood}...")

                people_to_immune = [p for p in neighborhoods[index_of_max].get_people()
                 if (self.can_immune(p.get_disease_state())) and
                 (p.get_age_category() > self.min_age_to_immune) and
                 (p.get_age_category() <= self.max_age_to_immune)]
                people_to_immune.sort(key=self.get_age_category,
                                      reverse=self.immune_strategy.get_order() == ImmuneStrategy.DESCENDING)

            elif self.immune_strategy.is_by_households():
                households = [h for h in self.parent._world.get_all_city_households()]
                for h in households:
                    if self.immune_strategy.is_immune_everybody_in_the_house():
                        # if one person can be vaccinated in this household, vaccinate ALL the eligible people
                        if seq(h.get_people()).count(
                                lambda p: self.can_immune(p.get_disease_state()) and
                                          (p.get_age_category() > self.state_min_age_to_immune) and
                                          (p.get_age_category() <= self.state_max_age_to_immune)) > 0:
                            people_to_immune += [p for p in h.get_people()
                                                 if (self.can_immune(p.get_disease_state())) and
                                                 (p.get_age_category() >= 18) and
                                                 (p.get_age_category() <= self.state_max_age_to_immune)]
                    else:
                        people_to_immune += [p for p in h.get_people()
                                             if (self.can_immune(p.get_disease_state())) and
                                             (p.get_age_category() > self.state_min_age_to_immune) and
                                             (p.get_age_category() <= self.state_max_age_to_immune)]
                    if len(people_to_immune) > self.max_people_to_immune_a_day:
                        break
            else:
                people_to_immune = [p for p in self.parent._world.all_people()
                                    if (self.can_immune(p.get_disease_state())) and
                                    (p.get_age_category() > self.state_min_age_to_immune) and
                                    (p.get_age_category() <= self.state_max_age_to_immune)]
            count_to_percentage = math.floor(max(0, target_percentage * can_be_immuned - immuned))
            print(f"ImmuneByAgeExtension({str(self.immune_strategy)}, (day {self.days_since_start}), " +
                  f"age {self.state_min_age_to_immune}-{self.state_max_age_to_immune}, immune {self.max_people_to_immune_a_day} a day, " +
                  f"immune % = {immuned}/{can_be_immuned} = {immuned_percentage * 100.0:.1f} count_to_percentage={count_to_percentage}")
            seq(people_to_immune).take(min(count_to_percentage, self.max_people_to_immune_a_day)).for_each(
                lambda person: self._register_events(person))

            # advance to the next age group only if you covered the current age group
            if len(people_to_immune) <= self.max_people_to_immune_a_day or \
                    immuned_percentage >= target_percentage:
                if self.immune_strategy.immune_by_neighborhood:
                    pass
                elif self.immune_strategy.get_order() == ImmuneStrategy.DESCENDING:
                    if self.state_min_age_to_immune <= self.min_age_to_immune:
                        self.finished = True
                    self.state_min_age_to_immune = max(self.state_min_age_to_immune - 10, self.min_age_to_immune)
                    self.state_max_age_to_immune -= 10
                elif self.immune_strategy.get_order() == ImmuneStrategy.ASCENDING:
                    if self.state_max_age_to_immune >= self.max_age_to_immune:
                        self.finished = True
                    self.state_max_age_to_immune = min(self.state_max_age_to_immune + 10, self.max_age_to_immune)
                    self.state_min_age_to_immune = self.state_max_age_to_immune - 10
                elif self.immune_strategy.get_order() == ImmuneStrategy.NONE:
                    pass  # do nothing
                else:
                    assert False, "immune_strategy is Out Of Range!"
            else:
                print(f"IMMUNE NOTHING people_to_immune={len(people_to_immune)} while self.max_people_to_immune_a_day={self.max_people_to_immune_a_day}\n"
                      f"immuned_percentage={immuned_percentage}, target_percentage={target_percentage}")
