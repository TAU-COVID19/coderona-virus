from datetime import timedelta
import os 
import json
from typing import List

from src.run_utils import INITIAL_DATE 
from src.seir import DiseaseState
from src.simulation.event import AddRoutineChangeEffect, AddRoutineChangeEnvironmentEffect, DayTrigger, DelayedEffect, DiseaseStateChangeEffect, EmptyTrigger,EmptyEffect,Event, RemoveRoutineChangeEffect
from src.simulation.interventions.intervention import quarantine_routine
from src.simulation.params import Params
from src.simulation.simulation import Simulation
from src.world import Person
from src.world.environments.household import Household
from src.world.world import World

# Test that the simple event still working 
def test_InitEvent():
    trigger = EmptyTrigger()
    EffectList = [EmptyEffect()]
    e = Event(trigger,EffectList)
    e.apply(None)

def test_2_effects_1_Person_NoTrigger():
    config_path = os.path.join(os.path.dirname(__file__),"..","src","config.json")
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        paramsDataPath = ConfigData['ParamsFilePath']
    Params.load_from(os.path.join(os.path.dirname(__file__),"..","src", paramsDataPath), override=True)

    PersonList = list(map(Person, [30]))
    trigger = EmptyTrigger()
    Effect_List1=[]

    for _person in PersonList: 
        Effect_List1.append(AddRoutineChangeEffect(
            person = _person, 
            routine_change_key = 'quarantine' , 
            routine_change_val = quarantine_routine(_person)))

        Effect_List1.append(RemoveRoutineChangeEffect(
            person = _person,
            routine_change_key = 'quarantine'))

    e = Event(trigger=trigger,effectLst = Effect_List1)
    e.apply(None)

    for person in PersonList:
        assert not bool(person.get_routine())

def test_1_DiseaseStateChangeEffect_2_Person_NoTrigger():
    config_path = os.path.join(os.path.dirname(__file__),"..","src","config.json")
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        paramsDataPath = ConfigData['ParamsFilePath']
    Params.load_from(os.path.join(os.path.dirname(__file__),"..","src", paramsDataPath), override=True)

    PersonList = list(map(Person, [30,20]))
    trigger = EmptyTrigger()
    Effect_List1=[]

    for _person in PersonList: 
        Effect_List1.append(
            DiseaseStateChangeEffect(
                person = _person,
                old_state = _person.get_disease_state(),
                new_state = DiseaseState.SYMPTOMATICINFECTIOUS,
        ))

    e = Event(trigger=trigger,effectLst = Effect_List1)
    e.apply(None)

    for person in PersonList:
        assert person.get_disease_state() == DiseaseState.SYMPTOMATICINFECTIOUS

def test_2_effects_3_Person_NoTrigger():
    config_path = os.path.join(os.path.dirname(__file__),"..","src","config.json")
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        paramsDataPath = ConfigData['ParamsFilePath']
    Params.load_from(os.path.join(os.path.dirname(__file__),"..","src", paramsDataPath), override=True)

    PersonList = list(map(Person, [30,35,40]))
    trigger = EmptyTrigger()
    Effect_List1=[]

    for _person in PersonList: 
        Effect_List1.append(AddRoutineChangeEffect(
            person = _person, 
            routine_change_key = 'quarantine' , 
            routine_change_val = quarantine_routine(_person)))

        Effect_List1.append(RemoveRoutineChangeEffect(
            person = _person,
            routine_change_key = 'quarantine'))

    e = Event(trigger=trigger,effectLst = Effect_List1)
    e.apply(None)

    for person in PersonList:
        assert not bool(person.get_routine())

def test_2_effects_3_Person_Trigger_True():
    config_path = os.path.join(os.path.dirname(__file__),"..","src","config.json")
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        paramsDataPath = ConfigData['ParamsFilePath']
    Params.load_from(os.path.join(os.path.dirname(__file__),"..","src", paramsDataPath), override=True)

    persons_arr = list(map(Person, [10,20,30]))
    assert len(persons_arr) == 3
    env_arr = []
    my_world = World(
        all_people = persons_arr,
        all_environments=env_arr,
        generating_city_name = "test",
        generating_scale = 1)

    my_simulation = Simulation(world = my_world, initial_date= INITIAL_DATE)
    
    trigger = DayTrigger(INITIAL_DATE)
    Effect_List1=[]

    for _person in persons_arr: 
        Effect_List1.append(AddRoutineChangeEffect(
            person = _person, 
            routine_change_key = 'quarantine' , 
            routine_change_val = quarantine_routine(_person)))

        Effect_List1.append(RemoveRoutineChangeEffect(
            person = _person,
            routine_change_key = 'quarantine'))

    e = Event(trigger=trigger,effectLst = Effect_List1)
    e.apply(my_simulation)

    for person in persons_arr:
        assert not bool(person.get_routine())

def test_2_effects_3_Person_Trigger_False():
    config_path = os.path.join(os.path.dirname(__file__),"..","src","config.json")
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        paramsDataPath = ConfigData['ParamsFilePath']
    Params.load_from(os.path.join(os.path.dirname(__file__),"..","src", paramsDataPath), override=True)

    persons_arr = list(map(Person, [10,20,30]))
    assert len(persons_arr) == 3
    env_arr = []
    my_world = World(
        all_people = persons_arr,
        all_environments=env_arr,
        generating_city_name = "test",
        generating_scale = 1)

    my_simulation = Simulation(world = my_world, initial_date= INITIAL_DATE)
    
    trigger = DayTrigger(INITIAL_DATE+timedelta(days=180))
    Effect_List1=[]

    for _person in persons_arr: 
        Effect_List1.append(AddRoutineChangeEffect(
            person = _person, 
            routine_change_key = 'quarantine' , 
            routine_change_val = quarantine_routine(_person)))

    e = Event(trigger=trigger,effectLst = Effect_List1)
    e.apply(my_simulation)

    for person in persons_arr:
        assert not bool(person.get_routine())

def test_1_delayedEffect_3_persons_delayed_not_reached():
    config_path = os.path.join(os.path.dirname(__file__),"..","src","config.json")
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        paramsDataPath = ConfigData['ParamsFilePath']
    Params.load_from(os.path.join(os.path.dirname(__file__),"..","src", paramsDataPath), override=True)

    persons_arr = list(map(Person, [10,20,30]))

    assert len(persons_arr) == 3
    env_arr = []
    my_world = World(
        all_people = persons_arr,
        all_environments=env_arr,
        generating_city_name = "test",
        generating_scale = 1)

    my_simulation = Simulation(world = my_world, initial_date= INITIAL_DATE)

    trigger = EmptyTrigger()
    
    Effect_List1=[]
    for _person in persons_arr: 
        Effect_List1.append(
            DiseaseStateChangeEffect(
                person = _person,
                old_state = _person.get_disease_state(),
                new_state = DiseaseState.SYMPTOMATICINFECTIOUS,
        ))

    e = Event(trigger=trigger,effectLst = Effect_List1)
    
    DelayedEvent = Event(
        EmptyTrigger(),
        [DelayedEffect(e, delay_time=timedelta(days=10))])

    DelayedEvent.apply(my_simulation)

    for person in persons_arr:
        assert person.get_disease_state() != DiseaseState.SYMPTOMATICINFECTIOUS

def test_1_delayedEffect_3_persons_delayed_reached():
    config_path = os.path.join(os.path.dirname(__file__),"..","src","config.json")
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        paramsDataPath = ConfigData['ParamsFilePath']
    Params.load_from(os.path.join(os.path.dirname(__file__),"..","src", paramsDataPath), override=True)

    persons_arr = list(map(Person, [10,20,30]))

    assert len(persons_arr) == 3
    env_arr = []
    my_world = World(
        all_people = persons_arr,
        all_environments=env_arr,
        generating_city_name = "test",
        generating_scale = 1)

    my_simulation = Simulation(world = my_world, initial_date= INITIAL_DATE)

    trigger = EmptyTrigger()
    
    Effect_List1=[]
    for _person in persons_arr: 
        Effect_List1.append(
            DiseaseStateChangeEffect(
                person = _person,
                old_state = _person.get_disease_state(),
                new_state = DiseaseState.SYMPTOMATICINFECTIOUS,
        ))

    e = Event(trigger=trigger,effectLst = Effect_List1)
    
    DelayedEvent = Event(
        EmptyTrigger(),
        [DelayedEffect(e, delay_time=timedelta(days=3))])

    DelayedEvent.apply(my_simulation)

    #move the simulation 3 days forword day by day to see where it happens
    my_simulation.simulate_day()
    my_simulation.simulate_day()
    my_simulation.simulate_day()
    my_simulation.simulate_day()

    for person in persons_arr:
        assert person.get_disease_state() == DiseaseState.SYMPTOMATICINFECTIOUS

def test_AddRoutineChangeEnvironmentEffect_2_peoples_diff_env():
    
    config_path = os.path.join(os.path.dirname(__file__),"..","src","config.json")
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        paramsDataPath = ConfigData['ParamsFilePath']
    Params.load_from(os.path.join(os.path.dirname(__file__),"..","src", paramsDataPath), override=True)

    #create diff enviroments
    h1 = Household(city = None,contact_prob_between_each_two_people=1)
    h2 = Household(city = None,contact_prob_between_each_two_people=1)
    persons_arr = [Person(10,[h1]),Person(20,[h1]),Person(30,[h2])]

    #register people to diff env
    h1.sign_up_for_today(persons_arr[0],1)
    h1.sign_up_for_today(persons_arr[1],1)
    h2.sign_up_for_today(persons_arr[2],1)
    
    assert len(h1.get_people()) == 2
    assert len(h2.get_people()) == 1

    env_arr = [h1,h2]
    my_world = World(
        all_people = persons_arr,
        all_environments=env_arr,
        generating_city_name = "test",
        generating_scale = 1,)

    my_simulation = Simulation(world = my_world, initial_date= INITIAL_DATE)

    trigger = EmptyTrigger()
    
    Effect_List1=[]
    Effect_List1.append(
        AddRoutineChangeEnvironmentEffect(
            environment=h1,
            routine_change_key="quarantine",
            routine_change_generator= quarantine_routine)
    )
    e = Event(trigger,Effect_List1)
    e.apply(my_simulation)
    assert "quarantine" in persons_arr[0].routine_changes.keys()
    assert "quarantine" in persons_arr[1].routine_changes.keys()
    assert "quarantine" not in persons_arr[2].routine_changes.keys()

def test_AddRoutineChangeEnvironmentEffect_And_RemoveRoutineChangeEnvironmentEffect_2_peoples_diff_env():
    
    config_path = os.path.join(os.path.dirname(__file__),"..","src","config.json")
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        paramsDataPath = ConfigData['ParamsFilePath']
    Params.load_from(os.path.join(os.path.dirname(__file__),"..","src", paramsDataPath), override=True)

    #create diff enviroments
    h1 = Household(city = None,contact_prob_between_each_two_people=1)
    h2 = Household(city = None,contact_prob_between_each_two_people=1)
    persons_arr = [Person(10,[h1]),Person(20,[h1]),Person(30,[h2])]

    #register people to diff env
    h1.sign_up_for_today(persons_arr[0],1)
    h1.sign_up_for_today(persons_arr[1],1)
    h2.sign_up_for_today(persons_arr[2],1)
    
    assert len(h1.get_people()) == 2
    assert len(h2.get_people()) == 1

    env_arr = [h1,h2]
    my_world = World(
        all_people = persons_arr,
        all_environments=env_arr,
        generating_city_name = "test",
        generating_scale = 1,)

    my_simulation = Simulation(world = my_world, initial_date= INITIAL_DATE)

    trigger = EmptyTrigger()
    
    Effect_List1=[
        AddRoutineChangeEnvironmentEffect(
            environment=h1,
            routine_change_key="quarantine",
            routine_change_generator= quarantine_routine),
        RemoveRoutineChangeEffect(
            person=persons_arr[0],
            routine_change_key="quarantine")
    ]
    e = Event(trigger,Effect_List1)
    e.apply(my_simulation)
    assert "quarantine" not in persons_arr[0].routine_changes.keys()
    assert "quarantine" in persons_arr[1].routine_changes.keys()
    assert "quarantine" not in persons_arr[2].routine_changes.keys()

