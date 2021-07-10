from datetime import timedelta
import os
import json

from src.world import Person
from src.run_utils import INITIAL_DATE
from src.seir import DiseaseState
from src.simulation.event import DayEvent
from src.simulation.params import Params

def test_immune_and_get_events1():
    config_path = os.path.join(os.path.dirname(__file__),"..","src","config.json")
    Expected  = -1
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        paramsDataPath = ConfigData['ParamsFilePath']
    Params.load_from(os.path.join(os.path.dirname(__file__),"..","src", paramsDataPath), override=True)

    p = Person(30)
    events =  p.immune_and_get_events(INITIAL_DATE , timedelta(days =  15), \
        ((DiseaseState.SUSCEPTIBLE,timedelta(10)),(DiseaseState.IMMUNE,timedelta(21))))
    print(events)
    assert len(events) == 2
    assert events[0]._date == INITIAL_DATE + timedelta(days = 10)
    assert events[1]._date == INITIAL_DATE + timedelta(days = 15)
        
def test_immune_and_get_events2():
    config_path = os.path.join(os.path.dirname(__file__),"..","src","config.json")
    Expected  = -1
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        paramsDataPath = ConfigData['ParamsFilePath']
    Params.load_from(os.path.join(os.path.dirname(__file__),"..","src", paramsDataPath), override=True)

    p = Person(30)
    events =  p.immune_and_get_events(INITIAL_DATE , timedelta(days =  20), \
        ((DiseaseState.SUSCEPTIBLE,timedelta(10)),(DiseaseState.LATENT,timedelta(5)), \
        (DiseaseState.SUSCEPTIBLE,None)))
    assert len(events) == 3
    assert events[0]._date == INITIAL_DATE + timedelta(days = 10)
    assert events[1]._date == INITIAL_DATE + timedelta(days = 15)
    assert events[2]._date == INITIAL_DATE + timedelta(days = 20)

def test_immune_and_get_events3():
    config_path = os.path.join(os.path.dirname(__file__),"..","src","config.json")
    Expected  = -1
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        paramsDataPath = ConfigData['ParamsFilePath']
    Params.load_from(os.path.join(os.path.dirname(__file__),"..","src", paramsDataPath), override=True)

    p = Person(30)
    events =  p.immune_and_get_events(INITIAL_DATE , timedelta(days =  20), \
        ((DiseaseState.SUSCEPTIBLE,timedelta(10)),(DiseaseState.LATENT,timedelta(5)),\
            (DiseaseState.ASYMPTOMATICINFECTIOUS,timedelta(5),(DiseaseState.SUSCEPTIBLE,None))))
    assert len(events) == 3

def test_immune_and_get_events4():
    config_path = os.path.join(os.path.dirname(__file__),"..","src","config.json")
    Expected  = -1
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        paramsDataPath = ConfigData['ParamsFilePath']
    Params.load_from(os.path.join(os.path.dirname(__file__),"..","src", paramsDataPath), override=True)

    p = Person(30)
    events =  p.immune_and_get_events(INITIAL_DATE , timedelta(days =  3), \
        ((DiseaseState.LATENT , timedelta(days=10)),(DiseaseState.INCUBATINGPOSTLATENT, timedelta(days=3))))
    assert len(events) == 2

