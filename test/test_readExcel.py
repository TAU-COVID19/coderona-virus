import pytest
import json
import os

from world.population_generation import population_loader
from world.city_data import get_city_list_from_dem_xls


def test_Init_haifa():
    file_path = os.path.dirname(__file__)+"\\..\\src\\config.json"
    with open(file_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        citiesDataPath = ConfigData['CitiesFilePath']
    pop = population_loader.PopulationLoader(citiesDataPath)
    City1 = pop.get_city_by_name('Haifa')
    assert City1 is not None


def test_Init_haifaParms():
    file_path = os.path.dirname(__file__)+"\\..\\src\\config.json"
    with open(file_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        citiesDataPath = ConfigData['CitiesFilePath']
    pop = population_loader.PopulationLoader(citiesDataPath)
    City1 = pop.get_city_by_name('Haifa')
    assert City1.region == 3
    assert City1.nafa == 31


def test_Init_SmallTown():
    file_path = os.path.dirname(__file__)+"\\..\\src\\config.json"
    with open(file_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        citiesDataPath = ConfigData['CitiesFilePath']
    with pytest.raises(Exception):
        pop = population_loader.PopulationLoader(citiesDataPath)
        City1 = pop.get_city_by_name('Roah Midbar')


def test_Init_TownNotExist():
    file_path = os.path.dirname(__file__)+"\\..\\src\\config.json"
    with open(file_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        citiesDataPath = ConfigData['CitiesFilePath']
    with pytest.raises(Exception):
        pop = population_loader.PopulationLoader(citiesDataPath)
        City1 = pop.get_city_by_name('lala')


def test_GetCities():
    #There are only 198 cities that we know all the needed data
    file_path = os.path.dirname(__file__) + "\\..\\src\\config.json"
    with open(file_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        citiesDataPath = ConfigData['CitiesFilePath']
    lst  = get_city_list_from_dem_xls(citiesDataPath)
    assert len(lst) == 198

