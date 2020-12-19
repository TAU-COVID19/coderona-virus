import random
import itertools
from datetime import date, timedelta

from src.seir import DiseaseState
from src.simulation.event import (
    Event,
    DayEvent,
    AddRoutineChangeEffect,
    RemoveRoutineChangeEffect,
    AddRoutineChangeEnvironmentEffect,
    RemoveRoutineChangeEnvironmentEffect,
    DelayedEffect,
    AndTrigger,
    AfterTrigger,
    TimeRangeTrigger,
    EmptyTrigger,
    OrTrigger
)
from src.world import Person, World
import inspect
from src.simulation.params import Params


def workplace_closure_routine(person: Person):
    """
    Create a routine change that represents a closure of the person's workplace.
    Here we try to represent the changing of the weight in the workplace environment as well as other environments,
    due to the closure.
    :param person: Person
    :return: routine change dict, keys are environment names, values are weight multipliers.
    """
    params = Params.loader()["interventions_routines"]["workplace_closure"]
    routine = {}
    for env_name in person.get_routine():
        if env_name == 'workplace':
            routine['workplace'] = params["workplace"]
        else:
            routine[env_name] = params["other"]
    return routine


def quarantine_routine(person: Person):
    """
    Create a routine change that represents a person being in quarantine.
    Here we try to represent the changing (decreasing of weights) of the weight in all the environment, due to the quarantine.
    :param person: Person
    :return: routine change dict, keys are environment names, values are weight multipliers.
    """
    params = Params.loader()["interventions_routines"]["quarantine"]
    return {env_name: params["all"] for env_name in person.get_routine()}


def social_distancing_routine(person: Person):
    """
    Create a routine change that represents a social distancing effect on a person routine.
    Here we try to represent the changing (decreasing/ increasing of weights) of the weight in all the environment,
    due to the closure.
    :param person: Person
    :return: routine change dict, keys are environment names, values are weight multipliers.
    """
    params = Params.loader()["interventions_routines"]["social_distancing"]
    routine = {}
    for env_name in person.get_routine():
        if env_name == 'household':
            routine['household'] = params["household"]
        elif env_name == 'workplace':
            routine['workplace'] = params["workplace"]
        elif env_name == 'school':
            routine[env_name] = params["school"]
        else:
            routine[env_name] = params["other"]
    return routine


def household_isolation_routine(person: Person):
    """
    Create a routine change that represents a person being in isolation at home.
    Here we try to represent the changing (decreasing/ increasing of weights) of the weight in all the environment,
    due to the person staying at home.
    :param person: Person
    :return: routine change dict, keys are environment names, values are weight multipliers.
    """
    params = Params.loader()["interventions_routines"]["household_isolation"]
    routine = {}
    for env_name in person.get_routine():
        if env_name == 'household':
            routine['household'] = params["household"]
        else:
            routine[env_name] = params["other"]
    return routine


def city_curfew_routine(person: Person, city_name):
    """
    Create a routine change that represents a city curfew effect on a person routine.
    Here we try to represent the changing (decreasing/ increasing of weights) of the weight in all the environment,
    due to the closure of the city.
    :param person: Person
    :return: routine change dict, keys are environment names, values are weight multipliers.
    """
    params = Params.loader()["interventions_routines"]["city_curfew"]
    routine = {}
    has_free_time = False
    for env_name, env in person._environments.items():
        if env._city is None:
            continue
        if not ((env._city.get_name() == city_name) ^ (person.get_city_name() == city_name)):
            continue
        else:
            routine[env_name] = params["out_of_city"]
            has_free_time = True
    if has_free_time:
        routine['household'] = params["in_city"]["household"]
        routine['city_community'] = params["in_city"]["city_community"]
        routine['neighborhood_community'] = params["in_city"]["neighborhood_community"]

    return routine


def make_routine_change_events(person, start_date, end_date, key, routine_generator, args=None):
    """
    Create events that make routine change that will be active during the given time range
    :param person: Person to be affected by new routine changes
    :param start_date: datetime.date date when the change will be added
    :param end_date: datetime.date date when the change will be removed
    :param key: str key to represent the routine change in the dict on person
    :param routine_generator: function that creates the routine change dict, for person
    :param args: extra args for the routine_generator, like age
    :return: list of new events
    """
    if args is None:
        new_routine = routine_generator(person)
    else:
        new_routine = routine_generator(person, args)
    ret = [DayEvent(
        date=start_date,
        effect=AddRoutineChangeEffect(
            person=person,
            routine_change_key=key,
            routine_change_val=new_routine
        )
    ), DayEvent(
        date=end_date,
        effect=RemoveRoutineChangeEffect(
            person=person,
            routine_change_key=key,
        )
    )]
    return ret

class Intervention(object):
    """
    This class implements the API of configuring different interventions to
    When the simulation starts, it calls intervention.generate_events(world) (for each intervention),
    and the Intervention creates events,
    some it hooks on person state changes and some are DayEvents which it returns and the simulation then hooks on itself.
    """
    __slots__ = ('compliance', 'start_date', 'duration', 'end_date')

    def __init__(self, compliance: float, start_date: date, duration: timedelta):
        self.compliance = compliance
        self.start_date = start_date
        self.end_date = start_date + duration
        self.duration = duration

    def generate_events(self, world: World):
        """
        Every sub class has to implement this func.
        The simulation calls this func to generate all the events that make the intervention influence the run,
        and adds them to the events dict.
        :param world: World object, to access environments and population
        :return: list of Event object to register
        """
        raise NotImplementedError()

    def attributes(self):
        """
        This gets all public attributes, for making summery files
        :return: dict of attributes and values
        """
        attributes = {name: value for name, value in
                inspect.getmembers(self, lambda value: not inspect.ismethod(value))
                if not name.startswith('_')}
        attributes['duration'] = self.duration.days
        return attributes

    def __str__(self):
        attr = self.attributes()
        params_strings = ["{}={}".format(key, value) for (key, value) in attr.items()]
        return "{}({})".format(type(self).__name__, ", ".join(params_strings))

    def __eq__(self, other):
        return self.attributes() == other.attributes() and type(self) == type(other)


class TimedIntervention(Intervention):
    """
    Implementation of an intervention, that is time range based. Meaning, it happens between from some start date,
    for example, school closure on the 1.5 for 40 days
    """
    __slots__ = ('_key', '_routine_generator', '_args')

    def __init__(
            self,
            start_date: date,
            duration: timedelta,
            compliance: float,
            key: str,
            routine_generator,
            args=None
    ):
        super(TimedIntervention, self).__init__(compliance, start_date, duration)
        self._key = key
        self._routine_generator = routine_generator
        self._args = args

    def _condition(self, x):
        """
        Has to be implemented by each subclass
        :param x: person usually
        :return: True if the given person is relevent for this intervention, for example an elder person, or school kid.
        """
        raise NotImplementedError()

    def generate_events(self, world: World):
        """
        generated events that add the relevent routine change to the people that are relevant for this intervention,
        and events that remove it after that given duration.
        :param world: World object
        :return: list of Event objects
        """
        new_events = []
        for person in world.all_people():
            if self._condition(person):
                if random.random() < self.compliance:
                    curr_events = make_routine_change_events(
                        person,
                        self.start_date,
                        self.end_date,
                        self._key,
                        self._routine_generator,
                        self._args
                    )
                    for event in curr_events:
                        new_events.append(event)
        return new_events


class WorkplaceClosureIntervention(TimedIntervention):
    """
    Implements workplace closure that is time based.
    The intervention is relevant for all working people.
    """
    __slots__ = ()

    def __init__(self, start_date: date, duration: timedelta, compliance: float):
        super(WorkplaceClosureIntervention, self).__init__(
            start_date, duration, compliance, 'workplace_closure',
            workplace_closure_routine
        )

    def _condition(self, person):
        return person.has_environment('workplace')


class SocialDistancingIntervention(TimedIntervention):
    """
    Implementation of Social distancing that is time based, and is activated on people in the given age range
    """
    __slots__ = ('min_age', 'max_age')

    def __init__(self, start_date: date, duration: timedelta, compliance: float, age_range: tuple):
        super(SocialDistancingIntervention, self).__init__(
            start_date, duration, compliance, 'social_distancing',
            social_distancing_routine
        )
        self.min_age, self.max_age = age_range

    def _condition(self, x):
        return self.min_age <= x.get_age() <= self.max_age


class ElderlyQuarantineIntervention(TimedIntervention):
    """
    Implementation of Elderly Quarantine that is time based, and is activated on people older than the given age.
    """
    __slots__ = ('_min_age',)

    def __init__(self, start_date: date, duration: timedelta, compliance: float, min_age: int):
        super(ElderlyQuarantineIntervention, self).__init__(
            start_date, duration, compliance, 'quarantine',
            quarantine_routine
        )
        self._min_age = min_age

    def _condition(self, x):
        return x.get_age() >= self._min_age


class CityCurfewIntervention(TimedIntervention):
    """
    Implementation of city closure that is time based, and is activated on people in the given city (living or working)
    """
    __slots__ = ("city_name",)

    def __init__(self, city_name, start_date: date, duration: timedelta, compliance: float):
        super(CityCurfewIntervention, self).__init__(
            start_date, duration, compliance, 'city_curfew',
            city_curfew_routine, args=city_name
        )
        self.city_name = city_name

    def _condition(self, x):
        if all(env._city.get_name() != self.city_name for env in x._environments.values()):
            return False
        if all(env._city.get_name() == self.city_name for env in x._environments.values()):
            return False
        return True


class SymptomaticIsolationIntervention(Intervention):
    """
    Implementation of a policy of isolating the symptomatic people in the simulation, for some given time.
    As some person starts to be symptomatic, the intervention is activated and a new routine is implied.
    The API also allows to have a delay between th symptoms and the isolation.
    """
    __slots__ = ('start_date', 'end_date', 'duration', 'delay')

    def __init__(
            self,
            compliance: float,
            start_date: date,
            duration: timedelta,
            delay=1  # arbitrary
    ):
        super(SymptomaticIsolationIntervention, self).__init__(compliance, start_date, duration)
        self.delay = delay

    def generate_events(self, world: World):
        """
        generate events that are applied on the person when his state changes to symptomatic,
        and add the isolation routine. After the given duration, an event will remove the change.
        :param world: World object
        :return: list of new Events to register on the simulation
        """
        ret = []
        for person in world.all_people():
            if random.random() < self.compliance:
                add_effect = AddRoutineChangeEffect(
                    person=person,
                    routine_change_key='quarantine',
                    routine_change_val=quarantine_routine(person)
                )
                states = (
                    DiseaseState.INCUBATINGPOSTLATENT,
                    DiseaseState.SYMPTOMATICINFECTIOUS
                )
                person._init_event(*states)
                add_trigger = AndTrigger(
                    AfterTrigger(person.state_to_events[states]),
                    TimeRangeTrigger(self.start_date, self.end_date)
                )
                add_event = Event(
                    add_trigger, add_effect
                )
                day_event = DayEvent(self.start_date)  # Wasteful in memory!
                day_event.hook(add_event)
                ret.append(day_event)
                if self.delay != 0:
                    delay_time = timedelta(self.delay)
                    person.hook_on_change(
                        states,
                        Event(
                            EmptyTrigger(),
                            DelayedEffect(add_event, delay_time)
                        )
                    )
                else:
                    person.hook_on_change(states, add_event)

                remove_effect = RemoveRoutineChangeEffect(
                    person=person, routine_change_key='quarantine'
                )
                state_changes = list(itertools.product(
                    [DiseaseState.SYMPTOMATICINFECTIOUS, DiseaseState.CRITICAL],
                    [DiseaseState.IMMUNE, DiseaseState.DECEASED]
                ))
                for states in state_changes:
                    person._init_event(*states)
                remove_trigger = AndTrigger(
                    OrTrigger([
                        AfterTrigger(person.state_to_events[states])
                        for states in state_changes
                    ]),
                    AfterTrigger(add_event)
                )
                remove_event = Event(remove_trigger, remove_effect)
                for states in state_changes:
                    person.hook_on_change(states, remove_event)
        return ret


class HouseholdIsolationIntervention(Intervention):
    """
    This intervention create family isolation events for each symptomatic case.
    When the person get symptoms, the event that is triggered adds changes to his whole house.

    :param delay_on_enter: days to wait from symptoms to start quarantine.
    :param delay_on_exit: days to wait before exit from quarantine.
    :param is_exit_after_recovery: 
        if False stays in quarantine for delay_on_exit days.
        if True stays in quarantine up to total recovery(or death)
        and only then wait for delay_on_exit days. 
    """
    __slots__ = (
        'delay_on_enter',
        'delay_on_exit',
        'is_exit_after_recovery'
    )

    def __init__(
        self,
        compliance: float,
        start_date: date,
        duration: timedelta,
        delay_on_enter=1,  # arbitrary
        delay_on_exit=14,  # arbitrary
        is_exit_after_recovery=False
    ):
        super(HouseholdIsolationIntervention, self).__init__(compliance, start_date, duration)
        self.delay_on_enter = timedelta(delay_on_enter)
        self.delay_on_exit = timedelta(delay_on_exit)
        self.is_exit_after_recovery = is_exit_after_recovery

    def generate_events(self, world: World):
        """
        generate events that are applied on the person when his state changes to symptomatic,
        and add the isolation routine to the whole house. After the given duration and params,
        an event will remove the change.
        :param world: World object
        :return: list of new Events to register on the simulation
        """
        ret = []
        for person in world.all_people():
            if random.random() < self.compliance:
                household_environment = person.get_environment('household')
                add_effect = AddRoutineChangeEnvironmentEffect(
                    environment=household_environment,
                    routine_change_key='household_isolation',
                    routine_change_generator=household_isolation_routine
                )
                states = (
                    DiseaseState.INCUBATINGPOSTLATENT,
                    DiseaseState.SYMPTOMATICINFECTIOUS
                )
                person._init_event(*states)
                add_trigger = AndTrigger(
                    AfterTrigger(person.state_to_events[states]),
                    TimeRangeTrigger(self.start_date, self.end_date)
                )
                add_event = Event(
                    add_trigger, add_effect
                )
                day_event = DayEvent(self.start_date)  # Wasteful in memory!
                day_event.hook(add_event)
                ret.append(day_event)
                if self.delay_on_enter:
                    delay_time = self.delay_on_enter
                    person.hook_on_change(
                        states,
                        Event(
                            EmptyTrigger(),
                            DelayedEffect(add_event, delay_time)
                        )
                    )
                else:
                    person.hook_on_change(states, add_event)

                remove_effect = RemoveRoutineChangeEnvironmentEffect(
                    environment=household_environment, routine_change_key='household_isolation'
                )
                if self.is_exit_after_recovery:
                    state_changes = list(itertools.product(
                        [DiseaseState.SYMPTOMATICINFECTIOUS, DiseaseState.CRITICAL],
                        [DiseaseState.IMMUNE, DiseaseState.DECEASED]
                    ))
                    for states in state_changes:
                        person._init_event(*states)
                    remove_trigger = AndTrigger(
                        OrTrigger([
                            AfterTrigger(person.state_to_events[states])
                            for states in state_changes
                        ]),
                        AfterTrigger(add_event)
                    )
                    remove_event = Event(
                        remove_trigger,
                        DelayedEffect(Event(effect=remove_effect), self.delay_on_exit)
                    )
                    for states in state_changes:
                        person.hook_on_change(states, remove_event)
                else:
                    remove_trigger = AfterTrigger(add_event)
                    remove_event = Event(
                        remove_trigger,
                        DelayedEffect(Event(effect=remove_effect), self.delay_on_exit)
                    )
                    add_event.hook(remove_event)
        return ret
