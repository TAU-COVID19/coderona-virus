import json
from logging import exception
import math
import multiprocessing as mp
import os
import pytest
import sys 

from src.logs import Statistics
from src.simulation.params import Params
from src.simulation.initial_infection_params import NaiveInitialInfectionParams
from src.run_utils import generate_all_cities_for_jobs,SimpleJob, run
from src.world.population_generation import PopulationLoader
from src.world.city_data import get_city_list_from_dem_xls


def test_Init_haifa(cities_path):
    population_loader = PopulationLoader(
            citiesDataPath,
            added_description="",
            with_caching=False,
            verbosity=False
        )
    world = population_loader.get_world(city_name='Haifa', scale=1,is_smart= False)
    assert world is not None


def test_Init_haifaParms(cities_path):
    pop = population_loader.PopulationLoader(cities_path)
    City1 = pop.get_city_by_name('Haifa')
    assert City1.region == 3
    assert City1.nafa == 31

def test_GetCities():
    #There are only 198 cities that we know all the needed data
    lst  = get_city_list_from_dem_xls(cities_path)
    assert len(lst) == 198

def test_generate_all_cities_for_jobs_parallel():
    citiesDataPath = ""
    params_to_change = {
        ("disease_parameters", "infectiousness_per_stage", "critical"): 1
    }
    test_jobs = [
        SimpleJob("test_default", 'kefar yona', 1.0,params_to_change=params_to_change),
        SimpleJob("test_default2", 'kefar yona', 1.0,params_to_change=params_to_change),
        SimpleJob("test_default3", 'kefar yona', 1.0,params_to_change=params_to_change)]  
    generate_all_cities_for_jobs(jobs=test_jobs,cpus_to_use=int(math.floor(mp.cpu_count()*0.9)))
    
def test_generate_all_cities_for_jobs_serial(params, cities_path):

    population_loader = PopulationLoader(
            cities_path,
            added_description="",
            with_caching=False,
            verbosity=False
        )
    world = population_loader.get_world(city_name='Atlit', scale=1,is_smart= False)
    assert len(world.all_people()) > 0

