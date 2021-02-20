from datetime import date
import random
from numpy.lib.function_base import median
from src.world.environments.homogeneous_environment import HomogeneousEnvironment
from src.simulation.params import Params
from src.world.person import Person
from src.seir.disease_state import DiseaseState

def test_propagate_infection(params_path):
    """
    tests the consistency of the propagate_infection function in HomogenousEnvironment
    """
    Params.load_from(params_path)
    DiseaseState.init_infectiousness_list()
    percent_infected = 0.1
    contact_prob = 0.25
    num_of_people = 400
    weight_list = [max(0.3, random.random()-0.1) for _ in range(num_of_people)]
    env = HomogeneousEnvironment(contact_prob, "test")
    total = 0
    infections = []
    loops = 100
    for _ in range(loops):
        env._person_dict = {Person(random.randint(20, 60)):weight_list[i] for i in range(num_of_people)}
        for p, w in env._person_dict.items():
            if percent_infected < random.random():
                p._disease_state = DiseaseState.ASYMPTOMATICINFECTIOUS
            else:
                p._disease_state = DiseaseState.SUSCEPTIBLE
            p._change()
            env.sign_up_for_today(p, w)
        num_of_infections = len(env.propagate_infection(date(2020,12,1)))
        infections.append(num_of_infections)
        total += num_of_infections
    avg = total/loops
    assert abs(avg - median(infections)) < 10
