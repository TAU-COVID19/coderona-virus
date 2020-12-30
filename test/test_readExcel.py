from src.world.population_generation import population_loader
import pytest
import json
import os

def test_Init():
    file_path = os.path.dirname(__file__)+"\\..\\src\\config.json"
    print(file_path)
    with open(file_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        citiesDataPath = ConfigData['CitiesFilePath']
    pop = population_loader.PopulationLoader(citiesDataPath)
    City1 = pop.get_city_by_name('Haifa')
    assert City1 is not None

