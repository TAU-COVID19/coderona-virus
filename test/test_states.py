import os
import json
import random
from functools import cmp_to_key
from src.logs.summary import TableFormat
from src.simulation.event import Event
from collections import Counter
from test.conftest import helpers
from src.seir.seir_times import daysdelta
from src.run_utils import INITIAL_DATE 
from src.seir import DiseaseState
from src.simulation.params import Params
from src.simulation.simulation import Simulation,ORDER
from src.world import Person
from src.world.environments.household import Household
from src.world.population_generation import population_loader
from src.world.population_generation import generate_city
from src.world.world import World

#Test the amount of the  created Immune
def test_CreateDeltaFile(helpers):
    helpers.clean_outputs()
    config_path = os.path.join(os.path.dirname(__file__),"..","src","config.json")
    Expected  = -1
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        paramsDataPath = ConfigData['ParamsFilePath']
    Params.load_from(os.path.join(os.path.dirname(__file__),"..","src", paramsDataPath), override=True)

    ageList = [random.randint(0,40) for i in range(10)]
    PersonList = list(map(Person, ageList))
    events_acc = []
    for person in PersonList:
        states_table = ((DiseaseState.LATENT,daysdelta(3)),
                        (DiseaseState.ASYMPTOMATICINFECTIOUS,daysdelta(3)),
                        (DiseaseState.IMMUNE, daysdelta(3)),
                        (DiseaseState.IMMUNE, None))
        events = person.gen_and_register_events_from_seir_times(date = INITIAL_DATE,states_and_times= states_table)
        events_acc += events
        # person.set_disease_state(DiseaseState.LATENT)
    env_arr = []
    my_world = World(
        all_people = PersonList,
        all_environments=env_arr,
        generating_city_name = "test",
        generating_scale = 1)

    my_simulation = Simulation(world = my_world, initial_date= INITIAL_DATE)
    my_simulation.register_events(events_acc)
    my_simulation.run_simulation(num_days=10,name="test")
    #assert events dictionary is not empty
    tbl,txt = my_simulation.stats.get_state_stratified_summary_table(table_format=TableFormat.CSV)
    assert len(tbl)==7
    assert tbl[0][0] == INITIAL_DATE
    assert tbl[0][1][DiseaseState.SUSCEPTIBLE] == 10
    assert tbl[1][0] == INITIAL_DATE + daysdelta(days=1)
    assert tbl[1][1] == Counter() 
    assert tbl[2][0] == INITIAL_DATE + daysdelta(days=2)
    assert tbl[2][1] == Counter() 
    assert tbl[3][0] == INITIAL_DATE + daysdelta(days=3)
    assert tbl[3][1][DiseaseState.ASYMPTOMATICINFECTIOUS] == 10
    assert tbl[4][0] == INITIAL_DATE + daysdelta(days=4)
    assert tbl[4][1] == Counter() 
    assert tbl[5][0] == INITIAL_DATE + daysdelta(days=5)
    assert tbl[5][1] == Counter() 
    assert tbl[6][0] == INITIAL_DATE + daysdelta(days=6)
    assert tbl[6][1][DiseaseState.IMMUNE] == 10
    