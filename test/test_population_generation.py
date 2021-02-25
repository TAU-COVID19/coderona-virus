from src.simulation.params import Params
from src.world.population_generation import population_loader
from src.world.population_generation import generate_city


def test_CityGeneration(params_path, cities_path):
    Params.load_from(params_path)
    pop = population_loader.PopulationLoader(cities_path)
    tmp_city = pop.get_city_by_name('Haifa')
    city = generate_city(tmp_city,
                         True,
                         internal_workplaces=True,
                         scaling=1.0,
                         verbosity=False,
                         to_world=True)

    humans = city.all_people()
    assert abs(283637 - len(humans)) < 5
    assert len(city.get_all_city_communities()) == 1
    assert city.get_person_from_id(humans[0]._id) is not None
