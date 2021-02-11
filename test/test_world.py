import os
import json
import pytest
from src.world import person
from src.seir import DiseaseState

#Test the amount of the  created Immune
def test_createInfectedPersons():
    config_path = os.path.dirname(__file__)+"/../src/config.json"
    Expeced  = -1
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        Expeced = float(ConfigData["R0_percent"])
    assert Expeced >= 0 
    cnt = 0
    for i in range(0,100):
        tmp = person.Person(7)
        if tmp.last_state == DiseaseState.IMMUNE:
            cnt =cnt + 1
    tmp = cnt / 100
    #Assert that the amount of people that created in recovered state are 
    # within 5 percent of expected
    assert tmp > Expeced - 0.05
    assert tmp < Expeced + 0.05





