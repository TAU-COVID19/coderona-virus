import os
import json
from collections import Counter

from src.seir import DiseaseState,sample_seir_times,machine_type,RealDataSeirTimesGeneration,SIRS
from src.simulation.params import Params
from src.world import Person

#Test the amount of the  created Immune
def test_create_SIR_machine():
    config_path = os.path.join(os.path.dirname(__file__),"..","src","config.json")
    Expected  = -1
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        paramsDataPath = ConfigData['ParamsFilePath']
    Params.load_from(os.path.join(os.path.dirname(__file__),"..","src", paramsDataPath), override=True)

    #Assert able to create statte machines properly
    a= RealDataSeirTimesGeneration.make()
    assert isinstance(a,RealDataSeirTimesGeneration)

def test_create_SIRS_machine():
    config_path = os.path.join(os.path.dirname(__file__),"..","src","config.json")
    Expected  = -1
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        paramsDataPath = ConfigData['ParamsFilePath']
    Params.load_from(os.path.join(os.path.dirname(__file__),"..","src", paramsDataPath), override=True)

    b= SIRS.make()
    assert isinstance(b,SIRS)

def test_sample_SIRS_seirs_times():
    config_path = os.path.join(os.path.dirname(__file__),"..","src","config.json")
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        paramsDataPath = ConfigData['ParamsFilePath']
    Params.load_from(os.path.join(os.path.dirname(__file__),"..","src", paramsDataPath), override=True)

    curr_machine_type = machine_type["SIRS"]
    p=Person(94)
    final_states = []
    for i in range(1000):
        table = sample_seir_times(curr_machine_type,p)
        assert table[0][0] == DiseaseState.LATENT
        final_states.append(table[-1][0])
    cnt_table  = Counter(final_states)
    assert DiseaseState.IMMUNE in cnt_table.keys()
    assert DiseaseState.DECEASED in cnt_table.keys()
    assert DiseaseState.SUSCEPTIBLE in cnt_table.keys()
    assert len(cnt_table.keys())==3 