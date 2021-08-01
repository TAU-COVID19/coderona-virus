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
        num_of_infections = len(env.propagate_infection(date(year = 2020,month = 12,day = 1)))
        infections.append(num_of_infections)
        total += num_of_infections
    avg = total/loops
    assert abs(avg - median(infections)) < 10

def test_single_person_infected_contact_half(params_path):
    """
    Tests that if we have only one person that is sick but he is in confinement,
    he won't infect a single person with contact_prob = 0.5
    """
    Params.load_from(params_path)
    DiseaseState.init_infectiousness_list()
    contact_prob = 0.5
    num_of_people = 400
    weight_list = [max(0.3, random.random()-0.1) for _ in range(num_of_people)]
    env = HomogeneousEnvironment(contact_prob, "test")
    infections = []
    
    
    env._person_dict = {Person(random.randint(20, 60)):weight_list[i] for i in range(num_of_people)}
    last_person = None
    for p, w in env._person_dict.items():
        p._disease_state = DiseaseState.SUSCEPTIBLE
        p._change()
        env.sign_up_for_today(p, w)
        last_person = p
    last_person._disease_state = DiseaseState.ASYMPTOMATICINFECTIOUS
    last_person._infectiousness_prob = 0 
    last_person._change()
    env.sign_up_for_today(p, w)


    num_of_infections = len(env.propagate_infection(date(year = 2020,month = 12,day = 1)))
    infections.append(num_of_infections)
    
    assert num_of_infections == 0 

def test_single_person_infected_contact1(params_path):
    """
    Tests that if we have only one person that is sick but he is in confinement,
    he won't infect a single person with contact_prob = 1
    """
    Params.load_from(params_path)
    DiseaseState.init_infectiousness_list()
    contact_prob = 1
    num_of_people = 400
    weight_list = [max(0.3, random.random()-0.1) for _ in range(num_of_people)]
    env = HomogeneousEnvironment(contact_prob, "test")
    infections = []
    
    
    env._person_dict = {Person(random.randint(20, 60)):weight_list[i] for i in range(num_of_people)}
    last_person = None
    for p, w in env._person_dict.items():
        p._disease_state = DiseaseState.SUSCEPTIBLE
        p._change()
        env.sign_up_for_today(p, w)
        last_person = p
    last_person._disease_state = DiseaseState.ASYMPTOMATICINFECTIOUS
    last_person._infectiousness_prob = 0 
    last_person._change()
    env.sign_up_for_today(p, w)


    num_of_infections = len(env.propagate_infection(date(year = 2020,month = 12,day = 1)))
    infections.append(num_of_infections)
    
    assert num_of_infections == 0 
