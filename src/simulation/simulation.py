import logging
import os
import random as _random
from collections import Counter
from datetime import timedelta
from copy import deepcopy

from src.simulation.event import DayEvent
from src.logs import Statistics, DayStatistics
from src.world import Person
from src.world.environments import InitialGroup
from src.debuggers import *


log = logging.getLogger(__name__)


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

    def __init__(
        self,
        world,
        initial_date,
        interventions=None,
        stop_early=None,
        verbosity=False,
        outdir=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
    ):
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
        # check(desc='Sim 75')
        # # attributes relevant for computing R data
        self.stop_early = stop_early
        self.last_day_to_record_r = None
        self.num_r_days = None
        # check(desc='Sim 80')
        if self.stop_early is not None:
            name_stop, self.num_r_days = self.stop_early
            self.last_day_to_record_r = initial_date + timedelta(days=self.num_r_days)
            assert name_stop == "r", "Other premature stops are not yet supported"
        self.first_infectious_people = set()
        # check(desc='Sim 85')
        self.initial_infection_doc = None
        self.num_days_to_run = None

        # save all the events that create the interventions behavior on the simulation
        for inter in self.interventions:
            check(desc='Sim 92')
            self.register_events(inter.generate_events(self._world))
        print('Initialized Simulation', get_mem())

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
        # check(desc='Sim 113')

        for individual in changed_population:
            individual.register_to_daily_environments()

        for env in self._world.all_environments:
            self.register_events(env.propagate_infection(self._date))
        # check(desc='Sim 120')
                    
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
        # check(desc='Sim 137')

        self.stats.add_daily_data(daily_data)
        for person in changed_population:
            person.save_state()

        if self.last_day_to_record_r is not None and self._date <= self.last_day_to_record_r:
            for person in changed_population:
                if person.is_infected:
                    # check(desc='Sim 146')
                    self.first_infectious_people.add(person)
        self._date += timedelta(days=1)

    def register_event_on_day(self, event, date):
        """
        hook the given event to the given date, so in that day this event will happen.
        :param event: Event
        :param date: datetime Date
        """
        if date not in self._events:
            # check(desc='Sim 157')
            self._events[date] = DayEvent(date)
        # check(desc='Sim 159')
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
            # check(desc='Sim 169')
            assert isinstance(event, DayEvent), \
                'Unexpected event type: {}'.format(type(event))
            self.register_event_on_day(event, event._date)

    def infect_random_set(self, num_infected, infection_doc, per_to_immune =0.0, city_name=None):
        """
        Infect a uniformly random initial set,
        so that the disease an spread during the simulation.
        :param num_infected: int number of infected to make
        :param infection_doc: str to doc the infection data
        (written to the inputs.txt file)
        :param city_name: the name of the city to infect
        (if left None, infects people from all around the World)
        """
        assert isinstance(num_infected, int)
        assert self.initial_infection_doc is None
        self.initial_infection_doc = infection_doc

        if city_name is not None:
            population = [p for p in self._world.all_people() if p.get_city_name() == city_name]
        else:
            population = self._world.all_people()
        assert 0 <= num_infected <= len(population), "Trying to infect {} people out of {}".format(num_infected, len(population))
        
        num_immuned = int(round(len(population)*per_to_immune))
        Selected_persons = _random.sample(population, num_infected + num_immuned)
        people_to_infect = Selected_persons[:num_infected]
        people_to_immune = Selected_persons[num_infected:]
        for person in people_to_infect:
            assert isinstance(person, Person), type(person)
            self.register_events(person.infect_and_get_events(self._date, InitialGroup.initial_group()))
        for person in people_to_immune:
            assert isinstance(person, Person), type(person)
            self.register_events(person.immune_and_get_events(self._date, InitialGroup.initial_group()))

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

    def run_simulation(
        self,
        num_days,
        name,
        datas_to_plot=None
    ):
        """
        This main loop of the simulation.
        It advances the simulation day by day and saves,
        and after it finishes it saves the output data to the relevant files.
        :param num_days: int - The number of days to run
        :param name: str - The name of this simulation, will determine output
        directory path and filenames.
        :param datas_to_plot: Indicates what sort of data we wish to plot
        and save at the end of the simulation.
        """
        check(desc='Sim 252')
        assert self.num_days_to_run is None
        self.num_days_to_run = num_days
        if datas_to_plot is None:
            datas_to_plot = dict()
        log.info("Starting simulation " + name)
        print('Sim', 250, get_mem())
        for day in range(num_days):
            self.simulate_day()
            if self.stats.is_static() or self.first_people_are_done():
                if self._verbosity:
                    log.info('simulation stopping after {} days'.format(day))
                break
        check(desc='Sim 265')
        self.stats.mark_ending(self._world.all_people())
        self.stats.calc_r0_data(self._world.all_people(), self.num_r_days)
        self.stats.dump('statistics.pkl')
        for name, data_to_plot in datas_to_plot.items():
            self.stats.plot_daily_sum(name, data_to_plot)
        check(desc='Sim 271')
        self.stats.write_summary_file('summary')
        self.stats.write_summary_file('summary_long', shortened=False)
        if self.stats._r0_data:
            self.stats.plot_r0_data('r0_data_' + name)
        check(desc='Sim 276')
        self.stats.write_params()
        self.stats.write_inputs(self)
        self.stats.write_interventions_inputs_csv()
