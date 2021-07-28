from copy import deepcopy
from collections import Counter
from enum import Enum
from functools import cmp_to_key
import logging
import os
import random as random
from datetime import timedelta
from src.seir import seir_times
from src.seir.disease_state import DiseaseState
from src.simulation.event import DayEvent
from src.logs import Statistics, DayStatistics
from src.world import Person
from src.world.environments import InitialGroup,Household



log = logging.getLogger(__name__)

class ORDER(Enum):
    NONE =0,
    ASCENDING=1,
    DESCENDING=2,


def person_comperator_ASCENDING(a:Person,b:Person):
    """
    Compare persons by their age for ASCENDING sort
    """
    return a.get_age() - b.get_age()

def person_comperator_DESCENDING(a:Person,b:Person):
    """
    Compare persons by their age for DESCENDING sort
    """
    return b.get_age() - a.get_age()

def house_comperator_ASCENDING(a:Household,b:Household):
        """
        Compare households by their youngest person
        """
        #Get the persons we whish to sort 
        a_people = a.get_people()
        b_people = b.get_people()
        #Sort the persons by their age in ascending way 
        a_people = sorted(a_people,key = cmp_to_key(person_comperator_ASCENDING))
        b_people = sorted(b_people,key = cmp_to_key(person_comperator_ASCENDING))
        #compare the youngest persons of each house
        return a_people[0].get_age() - b_people[0].get_age()
    
def house_comperator_DESCENDING(a:Household,b:Household):
    """
    Compare households by their youngest person
    """
    #Get the persons we whish to sort 
    a_people = a.get_people()
    b_people = b.get_people()
    #Sort the persons by their age in ascending way 
    a_people = sorted(a_people,key = cmp_to_key(person_comperator_DESCENDING))
    b_people = sorted(b_people,key = cmp_to_key(person_comperator_DESCENDING))
    #compare the youngest persons of each house
    return b_people[0].get_age() - a_people[0].get_age()
    
    
class Simulation(object):
    """
    An object which runs a single simulation, holding a world,
    calling events and propagating infections throughout environments
    day by day.
    """
    __slots__ = (
        '_verbosity',
        '_world',
        '_date',
        '_initial_date',
        'interventions',
        '_events',
        'stats',
        'stop_early',
        'last_day_to_record_r',
        'num_r_days',
        'first_infectious_people',
        'initial_infection_doc',
        'num_days_to_run'
    )

    def __init__(self, world, initial_date, interventions=None, stop_early=None, verbosity=False,
                 outdir=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')):
        """
        :param world: The World object that this simulation will run on
        :param initial_date: The starting date for the simulation
        :param interventions: A list of the interventions applied in this simulation
        :param stop_early: An object that represent a condition which,
        when holds, causes the simulation to stop prematurely.
        Currently only one type of early stop supported, meant to help compute
        R0, R1, ..., Rk efficiently - stopping when all people infected in the
        first k days have recovered.
        :param verbosity: Whether or not this simulation should print debug info
        :param outdir: The path of the directory output files
        should be written into
        """
        if interventions is None:
            interventions = []
        self._verbosity = verbosity
        self._world = world
        self._date = initial_date
        self._initial_date = deepcopy(initial_date)
        self.interventions = interventions
        self._events = {}
        self.stats = Statistics(outdir, world)
        # It's important that we sign people up before we init interventions!
        self._world.sign_all_people_up_to_environments()
        for intervention in interventions:
            self.stats.add_intervention(intervention)

        # attributes relevant for computing R data
        self.stop_early = stop_early
        self.last_day_to_record_r = None
        self.num_r_days = None
        if self.stop_early is not None:
            name_stop, self.num_r_days = self.stop_early
            self.last_day_to_record_r = initial_date + timedelta(days=self.num_r_days)
            assert name_stop == "r", "Other premature stops are not yet supported"
        self.first_infectious_people = set()

        self.initial_infection_doc = None
        self.num_days_to_run = None

        # save all the events that create the interventions behavior on the simulation
        for inter in self.interventions:
            self.register_events(inter.generate_events(self._world))

    def simulate_day(self):
        """
        Simulate one day of the simulation. Does this in four steps:
        1. Apply or remove registered events
        (either applying intervention effects or
        advancing the disease states of people)
        2. register people who changed weights to their environments
        3. spread the infection throughout the environments
        4. register the changes to the Statistics object
        """
        if self._date in self._events:
            self._events[self._date].apply(self)
            del self._events[self._date]

        changed_population = [
            person for person in self._world.all_people() if person._changed
        ]

        for individual in changed_population:
            individual.register_to_daily_environments()

        for env in self._world.all_environments:
            self.register_events(env.propagate_infection(self._date))

        changed_population = [
            person for person in self._world.all_people() if person._changed
        ]

        if self._verbosity and self._date.weekday() == 6:
            log.info("------ day-{}: disease state ------------".format(self._date))
            log.info(Counter([person.get_disease_state() for person in self._world.all_people()]))
            log.info("------ Infected by environments ----------")
            log.info(Counter([person.get_infection_data().environment.name for person in self._world.all_people() if
                              person.get_disease_state().is_infected() and person.get_infection_data()]))

        daily_data = DayStatistics(
            self._date,
            changed_population
        )
        self.stats.add_daily_data(daily_data)
        for person in changed_population:
            person.save_state()

        if self.last_day_to_record_r is not None and self._date <= self.last_day_to_record_r:
            for person in changed_population:
                if person.is_infected:
                    self.first_infectious_people.add(person)
        self._date += timedelta(days=1)

    def register_event_on_day(self, event, date):
        """
        hook the given event to the given date, so in that day this event will happen.
        :param event: Event
        :param date: datetime Date
        """
        if date not in self._events:
            self._events[date] = DayEvent(date)
        self._events[date].hook(event)

    def register_events(self, event_list):
        """
        Add all the given events to their dates on the simulation.
        This applies only to DayEvents that need to be triggered on a specific date.
        :param event_list: list of Event objects
        """
        if not isinstance(event_list, list):
            event_list = [event_list]
        for event in event_list:
            assert isinstance(event, DayEvent), \
                'Unexpected event type: {}'.format(type(event))
            self.register_event_on_day(event, event._date)


    def infect_random_set(self,num_infected :int, infection_doc :str, per_to_immune=0.0,Immune_compliance :float =1,order:ORDER = ORDER.NONE, city_name=None,min_age=0,people_per_day =1):
        """
        Infect a uniformly random initial set,
        so that the disease can spread during the simulation.
        :param num_infected: int number of infected to make
        :param per_to_immune: percent from the total population that should get immuned
        :param infection_doc: str to doc the infection data
        (written to the inputs.txt file)
        param oredr: specify if we order asending to descending the ages oof the persons that will get immuned 
        :param city_name: the name of the city to infect
        (if left None, infects people from all around the World)
        :param min_age: int specify the min age from which we start to infect population
        if the value is 0 we infect all the population \
        :param: Immune_compliance float. Simulate the state in which we aske some percentage of the population
        to get immune but only some of them agreed
        """
        assert Immune_compliance >= 0, "Immune_compliance can not be negative"
        assert isinstance(num_infected, int)
        assert self.initial_infection_doc is None
        self.initial_infection_doc = infection_doc
        if per_to_immune is None:
            per_to_immune = 0.0
        if city_name is not None:
            population = [p for p in self._world.all_people() \
                if (p.get_city_name() == city_name)]
        else:
            population = [p for p in self._world.all_people()]

        #Doing best effort to infect and immune the people in our world
        #after talking to Noam we first infect the ones we can and immune the rest
        num_infected = min(num_infected ,len(population))
        tmp_num_immuned = int(round(len(population) * per_to_immune * Immune_compliance))
        num_immuned = min(len(population) - num_infected,tmp_num_immuned)
        assert len(population) >= num_infected + num_immuned \
            , "Trying to immune:{} infect:{} people out of {}".format(num_immuned, num_infected, len(population))
        adults = [p for p in population if p.get_age() > min_age]
        used_adults =0 
        used_persons = {}
        #First set the people that aren't immune to be infected
        while num_infected > 0:
            Selected_persons = random.sample(population, num_infected)
            for p in Selected_persons:
                if (p.get_id() not in used_persons) and (p.get_disease_state() == DiseaseState.SUSCEPTIBLE): 
                    self.register_events(p.infect_and_get_events(self._date, InitialGroup.initial_group()))
                    num_infected = num_infected-1
                    used_persons[p.get_id()]=p
                    if p.get_age() > 0:
                        used_adults += 1

        num_immuned = min(len(adults)-used_adults,num_immuned )
        if order == ORDER.ASCENDING:
            adults = sorted(adults,key = cmp_to_key(person_comperator_ASCENDING))
        elif order == ORDER.DESCENDING:
            adults = sorted(adults,key = cmp_to_key(person_comperator_DESCENDING))
        else:
            adults = random.sample(adults,len(adults))
        #Second set- immune persons that are above min_age and we are able to immune
        Immuned_until_now =0 
        while Immuned_until_now < num_immuned: #we start to count from zero therefor we need one more person
            Selected_persons = adults[Immuned_until_now:]
            delta_days =0 
            immuned_today =0 
            for p in Selected_persons:
                if (p.get_id() not in used_persons) : 
                    self.register_events(p.immune_and_get_events(start_date = self._date, delta_time = timedelta(days =delta_days) ))
                    # print("immuning id:{} on {}".format(p.get_id(),self._date + timedelta(days =delta_days)))
                    num_immuned = num_immuned-1
                    used_persons[p.get_id()] = p
                    immuned_today += 1
                    Immuned_until_now += 1
                    if immuned_today == people_per_day:
                        delta_days += 1 
                        immuned_today = 0

    
    def immune_households_infect_others(self,num_infected : int, infection_doc : str, per_to_immune=0.0,Immune_compliance:float =1,Sort_order:ORDER = ORDER.NONE, city_name=None,min_age = 0,people_per_day =0 ):
        """
        Immune some percentage of the households in the population and infectimg a given percentage of the population
        so that the disease can spread during the simulation.
        :param num_infected: int number of infected to make
        :param infection_doc: str to document the infection data
        (written to the inputs.txt file)
        :param city_name: the name of the city to infect
        (if left None, infects people from all around the World)
        :param min_age: specify the min age from which we start to infect population
        if the value is 0 we infect all the population 
        :per_to_immune: percentage of the population that we are going to immune by housholds
        :people_per_day: how much houses per day we should immune
        :param: Immune_compliance float. Simulate the state in which we aske some percentage of the population
        to get immune but only some of them agreed
        """
        assert isinstance(num_infected, int)
        assert self.initial_infection_doc is None
        self.initial_infection_doc = infection_doc
        if per_to_immune is None:
            per_to_immune = 0.0
        if city_name is not None:
            tmp_households = [h for h in self._world.get_all_city_households() if h._city == city_name]
        else:
            tmp_households = [h for h in self._world.get_all_city_households()]
        
        households= []
        adults_cnt = 0 
        for h in tmp_households:
            cnt = len([p for p in h.get_people() if p.get_age() > min_age])
            if cnt > 0:
                households.append(h)
                adults_cnt += cnt
        if Sort_order == ORDER.NONE:
                households = random.sample(households,len(households))
        elif Sort_order ==  ORDER.ASCENDING:
                households = sorted(households,key=cmp_to_key(house_comperator_ASCENDING))
        elif Sort_order == ORDER.DESCENDING:
                households = sorted(households,key=cmp_to_key(house_comperator_DESCENDING))

        num_infected = min(self._world.num_people(),num_infected)
        #Immune only some percentage of adults, that agreed to be immuned
        cnt_people_to_immun = int(self._world.num_people() * per_to_immune *  Immune_compliance )
        used_persons = {}
        household_index =0 
        days_delta =0 
        
        if num_infected > 0:
            UnsafePersons = [p for p in self._world.all_people()]
            people_to_infect = random.sample(UnsafePersons, min(len(UnsafePersons),num_infected))
            for person in people_to_infect:
                # print("calling infect_and_get_events from immune_households_infect_others for id:{}".format(person.get_id()))
                self.register_events(person.infect_and_get_events(self._date, InitialGroup.initial_group()))
                used_persons[person.get_id()] = person
                # print("Infecting person id:{} on date:{}".format(person.get_id(),self._date))
        
        while (cnt_people_to_immun > 0) and (people_per_day > 0)and (household_index < len(households)):
            cnt_people_to_immun_today  = people_per_day
            while (cnt_people_to_immun_today > 0) and (household_index < len(households)):
                persons_to_immune = [ p for p in households[household_index].get_people() \
                    if (p.get_age() >= min_age) and (p.get_id() not in used_persons)]
                if Sort_order == ORDER.NONE:
                    cnt_immune_in_house =0
                    for i in range(min(len(persons_to_immune),cnt_people_to_immun_today)):
                        print("immuning person age:{}".format(persons_to_immune[i].get_age()))
                        self.register_events(persons_to_immune[i].immune_and_get_events(start_date = self._date, delta_time = timedelta(days=days_delta)))
                        used_persons[persons_to_immune[i].get_id()] = persons_to_immune[i]
                        # print("Immune person id:{} date:{}".format(persons_to_immune[i].get_id(),self._date + timedelta(days=days_delta)))
                        cnt_people_to_immun_today -= 1
                        cnt_people_to_immun -= 1
                        cnt_immune_in_house += 1 
                    if cnt_immune_in_house == len(persons_to_immune):
                        household_index += 1
                elif Sort_order in [ORDER.ASCENDING,ORDER.DESCENDING]:
                    i=0
                    cnt_immune_in_house =0
                    while i < min(len(persons_to_immune),cnt_people_to_immun_today):
                        print("immuning person age:{}".format(persons_to_immune[i].get_age()))
                        self.register_events(persons_to_immune[i].immune_and_get_events(start_date = self._date, delta_time = timedelta(days=days_delta)))
                        used_persons[persons_to_immune[i].get_id()] = persons_to_immune[i]
                        # print("Immune person id:{} date:{}".format(persons_to_immune[i].get_id(),self._date + timedelta(days=days_delta)))
                        cnt_people_to_immun_today -= 1
                        cnt_people_to_immun -= 1
                        cnt_immune_in_house += 1 
                        for j in range(i+1,min(len(persons_to_immune),cnt_people_to_immun_today)):
                            if (persons_to_immune[j] not in used_persons) and ((persons_to_immune[i].get_age() // 10) == (persons_to_immune[j].get_age() // 10)):
                                self.register_events(persons_to_immune[j].immune_and_get_events(start_date = self._date, delta_time = timedelta(days=days_delta)))
                                used_persons[persons_to_immune[j].get_id()] = persons_to_immune[j]
                                # print("Immune person id:{} date:{}".format(persons_to_immune[i].get_id(),self._date + timedelta(days=days_delta)))
                                cnt_people_to_immun_today -= 1
                                cnt_people_to_immun -= 1
                                cnt_immune_in_house += 1 
                                i += 1
                        if cnt_immune_in_house == len(persons_to_immune):
                            household_index += 1
            days_delta += 1

        

    def first_people_are_done(self):
        """
        chacks whether the people infected on the first “num_r_days” days
        are infected. We use this in simulations in which we try to compute R.
        When these people recover, we stop the simulation.
        """
        if self.stop_early is None:
            return False
        return all((not person.is_infected) for person in self.first_infectious_people)

    def infect_chosen_set(self, infection_datas, infection_doc):
        """
        Infect a chosen and specific set of people, given to the function, and register the events.
        :param infection_datas: list of (id, date, seit_times) for each person to infect
        :param infection_doc: str to doc the infection for inputs file
        """
        assert self.initial_infection_doc is None
        self.initial_infection_doc = infection_doc
        for person_id, infection_date, seir_times in infection_datas:
            p = self._world.get_person_from_id(person_id)
            events = p.infect_and_get_events(infection_date, InitialGroup.initial_group(), seir_times=seir_times)
            p.get_infection_data().date = None  # To avoid being asked to plot this date, which is out of our range
            self.register_events(events)

        original_date = self._date
        for date in sorted(self._events.keys()):
            if date < original_date:
                self._date = date
                self._events[date].apply(self)
                del self._events[date]
        self._date = original_date

    def run_simulation(self, num_days, name, datas_to_plot=None,run_simulation = None,extensionsList = None):
        """
        This main loop of the simulation.
        It advances the simulation day by day and saves,
        and after it finishes it saves the output data to the relevant files.
        :param num_days: int - The number of days to run
        :param name: str - The name of this simulation, will determine output
        directory path and filenames.
        :param datas_to_plot: Indicates what sort of data we wish to plot
        and save at the end of the simulation.
        :param Extension: user's class that contains function that is called at the end of each day
        """
        assert self.num_days_to_run is None
        self.num_days_to_run = num_days
        if datas_to_plot is None:
            datas_to_plot = dict()
        log.info("Starting simulation " + name)

        extensions = []
        if extensionsList != None:
            for ExtName in extensionsList:
                mod  = __import__('src.extensions.' + ExtName,fromlist=[ExtName])
                ExtensionType = getattr(mod,ExtName)
                extensions = extensions + [ExtensionType(self)]
            

        for day in range(num_days):
            for ext in extensions:
                ext.start_of_day_processing()

            self.simulate_day()
            #Call Extension function at the end of the day
            for ext in extensions:
                ext.end_of_day_processing()
                
            if self.stats.is_static() or self.first_people_are_done():
                if self._verbosity:
                    log.info('simulation stopping after {} days'.format(day))
                break
                

        self.stats.mark_ending(self._world.all_people())
        self.stats.calc_r0_data(self._world.all_people(), self.num_r_days)
        self.stats.dump('statistics.pkl')
        for name, data_to_plot in datas_to_plot.items():
            self.stats.plot_daily_sum(name, data_to_plot)
        self.stats.write_summary_file('summary')
        self.stats.write_summary_file('summary_long', shortened=False)
        if self.stats._r0_data:
            self.stats.plot_r0_data('r0_data_' + name)
        self.stats.write_params()
        self.stats.write_inputs(self)
        self.stats.write_interventions_inputs_csv()
        