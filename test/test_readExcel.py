import math
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor

from src.run_utils import generate_all_cities_for_jobs, SimpleJob
from src.world.population_generation import PopulationLoader
from src.world.city_data import get_city_list_from_dem_xls


def test_Init_haifa(params, cities_path):
    population_loader = PopulationLoader(
            cities_path,
            added_description="",
            with_caching=False,
            verbosity=False
        )
    world = population_loader.get_world(city_name='Haifa', scale=1,is_smart= False)
    assert world is not None


def test_Init_haifaParms(cities_path):
    pop = PopulationLoader(cities_path)
    City1 = pop.get_city_by_name('Haifa')
    assert City1.region == 3
    assert City1.nafa == 31

def test_GetCities(cities_path):
    #There are only 198 cities that we know all the needed data
    lst  = get_city_list_from_dem_xls(cities_path)
    assert len(lst) == 198

def test_generate_all_cities_for_jobs_parallel():
    params_to_change = {
        ("disease_parameters", "infectiousness_per_stage", "critical"): 1
    }
    test_jobs = [
        SimpleJob("test_default", 'kefar yona', 1.0,params_to_change=params_to_change),
        SimpleJob("test_default2", 'kefar yona', 1.0,params_to_change=params_to_change),
        SimpleJob("test_default3", 'kefar yona', 1.0,params_to_change=params_to_change)]
    with ProcessPoolExecutor(int(math.floor(mp.cpu_count()*0.9))) as executor:
        generate_all_cities_for_jobs(jobs=test_jobs, process_executor=executor)
    
def test_generate_all_cities_for_jobs_serial(params, cities_path):

    population_loader = PopulationLoader(
            cities_path,
            added_description="",
            with_caching=False,
            verbosity=False
        )
    world = population_loader.get_world(city_name='Atlit', scale=1,is_smart= False)
    assert len(world.all_people()) > 0

