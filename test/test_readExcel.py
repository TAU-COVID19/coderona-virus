import pytest
import json
import os

from src.world.population_generation import population_loader
from src.world.city_data import get_city_list_from_dem_xls


def test_Init_haifa(cities_path):
    pop = population_loader.PopulationLoader(cities_path)
    City1 = pop.get_city_by_name('Haifa')
    assert City1 is not None


def test_Init_haifaParms(cities_path):
    pop = population_loader.PopulationLoader(cities_path)
    City1 = pop.get_city_by_name('Haifa')
    assert City1.region == 3
    assert City1.nafa == 31


def test_Init_SmallTown(cities_path):
    with pytest.raises(Exception):
        pop = population_loader.PopulationLoader(cities_path)
        City1 = pop.get_city_by_name('Roah Midbar')


def test_Init_TownNotExist(cities_path):
    with pytest.raises(Exception):
        pop = population_loader.PopulationLoader(cities_path)
        City1 = pop.get_city_by_name('lala')


def test_GetCities(cities_path):
    #There are only 198 cities that we know all the needed data
    lst  = get_city_list_from_dem_xls(cities_path)
    assert len(lst) == 198

