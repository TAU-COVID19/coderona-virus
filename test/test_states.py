import os
import json
import random
from functools import cmp_to_key
from src.simulation.event import Event
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
    print(my_simulation.stats._days_data)
    for p in PersonList:
        assert p.get_disease_state() == DiseaseState.IMMUNE
    assert True