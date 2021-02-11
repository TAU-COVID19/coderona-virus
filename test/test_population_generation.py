import os
import json

from src.simulation.params import Params
from src.world.population_generation import population_loader
from src.world.population_generation import generate_city


def test_CityGeneration():
    file_path = os.path.dirname(__file__) + "\\..\\src\\config.json"
    with open(file_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        citiesDataPath = ConfigData['CitiesFilePath']
        paramsDataPath = ConfigData['ParamsFilePath']
    Params.load_from(os.path.join(os.path.dirname(__file__), paramsDataPath), override=True)
    pop = population_loader.PopulationLoader(citiesDataPath)
    tmp_city = pop.get_city_by_name('Haifa')
    city = generate_city(tmp_city,
                         True,
                         internal_workplaces=True,
                         scaling=1.0,
                         verbosity=False,
                         to_world=True)

    humans = city.all_people()
    assert len(humans) == 283637
    assert len(city.get_all_city_communities()) ==1
    assert city.get_person_from_id(humans[0]._id) is not None
