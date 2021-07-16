import logging
import json
import numpy as np
import os
from datetime import date, timedelta
from socket import gethostname
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) # Adding the src folder to PYTHONPATH

from src.scenarios import *
from src.seir import DiseaseState
from src.simulation.initial_infection_params import NaiveInitialInfectionParams, SmartInitialInfectionParams,InitialImmuneType
from src.logs import make_age_and_state_datas_to_plot
from src.simulation.params import Params
from src.run_utils import RepeatJob, SimpleJob, run
import src.util.seed as seed

seed.set_random_seed()
log = logging.getLogger(__name__)


def generate_scenario_name(city_name, scenario, initial_num_infected,initial_per_immuned,immune_source,min_age, compliance, ci_delay, hi_delay, symptomatic_probs_scale):
    return f"{city_name}_{scenario}_init_{initial_num_infected}_immune_percenage_{initial_per_immuned}" + \
    f"_comp_{compliance}_cidelay_{ci_delay}_hidelay_{hi_delay}_symsc_{symptomatic_probs_scale}_computerName_{gethostname()}" + \
    f"_immune_source_{immune_source}_min_age_{min_age}"

def get_rescaled_symptomatic_probs(symptomatic_probs_scale):
    current_probs = Params.loader()['disease_parameters']['symptomatic_given_infected_per_age']
    return [min(1, symptomatic_probs_scale * t) for t in current_probs]

def get_datas_to_plot():
    graphs = {
        "infected": [
            DiseaseState.SYMPTOMATICINFECTIOUS,
            DiseaseState.INCUBATINGPOSTLATENT,
            DiseaseState.LATENT,
            DiseaseState.CRITICAL,
            DiseaseState.ASYMPTOMATICINFECTIOUS
        ],
        "critical" : [
            DiseaseState.CRITICAL
        ],
        "susceptible": [
            DiseaseState.SUSCEPTIBLE
        ],
        "deceased": [
            DiseaseState.DECEASED
        ],
        "immuned": [
            DiseaseState.IMMUNE
        ]
    }
    return {'amit_graph': make_age_and_state_datas_to_plot(age_groups=((0, 19), (20, 59), (60, 99)),
                                                           disease_state_groups=list(graphs.items()))}

def main():
    """
    This is the main function that runs the simulation.
    here we are able to add different intervention, params, and more configurations to the run.
    This is an example for using the code in the project, and running different simulations of the disease.
    """
    # sets the logging output to be at debug level, meaning more output than a regular run
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    scenarios = {
        # "scenario_1": scenario_1_interventions,
        # "scenario_21": scenario_21_interventions,
        # "scenario_22": scenario_22_interventions,
        # "scenario_23": scenario_23_interventions,
        # "scenario_24": scenario_24_interventions,
        # "scenario_25": scenario_25_interventions,
        # "scenario_26": scenario_26_interventions,
        # "scenario_232": scenario_232_interventions,
        # "scenario_262": scenario_262_interventions,
        # "scenario_272": scenario_272_interventions,
        # "scenario_282": scenario_282_interventions,
        # "scenario_36": scenario_36_interventions,
        # "scenario_39": scenario_39_interventions,
        # "scenario_365": scenario_365_interventions,
        # "scenario_395": scenario_395_interventions
        #"reality1" : scenario_reality1
        #"check" : scenario_check
        #"reality2" : scenario_reality2
        #"reality3": scenario_reality3
        #"reality4": scenario_reality4
        #"no_interventions": no_interventions
        #"not_relaxing_interventions": not_relaxing_interventions
        #"grant_time1" : grant_time1,
        #"grant_time2" : grant_time2
        #"paper_1" : paper_1
        #"paper_2" : paper_2
        #"paper_3" : paper_3
        #"paper_4" : paper_4
        #"paper_5": paper_5
        #"paper_6": paper_6
        #"paper_7": paper_7
        # "paper_8": paper_8
        #"paper_2_comp_9": paper_2_comp_9
        # "noam_lockdown_scenario": noam_lockdown_scenario
        # "vaccinations_scenario_general": vaccinations_scenario_general
        # "vaccinations_scenario_households": vaccinations_scenario_households,
        "Empty_scenario" : Empty_scenario
    }

    datas_to_plot = get_datas_to_plot()

    # choosing the city and the scale of the run:
    # the city name and scale determine the city and the size proportion to take (use 'all' for entire country)
    # city_name, scale = 'holon', 1
    # city_name, scale = 'all', 0.01 # This means loading 1% of the entire country
    # city_name, scale = 'all', 0.1 # This means loading the entire country
    print("Running all simulations...")
    config_path = os.path.join(os.path.dirname(__file__) ,"config.json")
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        paramsDataPath = ConfigData['ParamsFilePath']

    Params.load_from(os.path.join(os.path.dirname(__file__), paramsDataPath), override=True)

    # we build a list of the jobs to run:
    # each job can be run as a different process, and the population generation will be done once
    # if caching option is on

    jobs = []
    for initial_percentage_immune in [0.0]:
        for people_per_day in [10]:
            for immune_source,min_age in [(InitialImmuneType.HOUSEHOLDS,18)]:#the options are:GENERAL_POPULATION,HOUSEHOLDS
                for initial_num_infected in [100]:
                    for city_name, scale in [("Atlit",1)]:
                        for compliance in [0.8]:
                            for ci_delay in [4]:
                                for hi_delay in [4]:                                
                                    for symptomatic_probs_scale in [1]:
                                        for scenario_name, intervention_scheme in scenarios.items():
                                            params_to_change= {
                                                    ('disease_parameters', 'symptomatic_given_infected_per_age'): get_rescaled_symptomatic_probs(symptomatic_probs_scale)
                                                }
                                            full_scenario_name = generate_scenario_name(city_name,
                                                                                            scenario_name,
                                                                                            initial_num_infected,
                                                                                            initial_percentage_immune,
                                                                                            immune_source,
                                                                                            min_age,
                                                                                            compliance,
                                                                                            ci_delay,
                                                                                            hi_delay,
                                                                                            symptomatic_probs_scale)
            #                                    full_scenario_name = "res"
                                            jobs.append(RepeatJob(SimpleJob(full_scenario_name,
                                                                                days=40,
                                                                                city_name=city_name,
                                                                                scale=scale,
                                                                                infection_params=NaiveInitialInfectionParams(initial_num_infected,per_to_Immune=initial_percentage_immune,immune_source = immune_source,min_age = min_age,people_per_day =people_per_day),
                                                                                #infection_params=SmartInitialInfectionParams(initial_num_infected, round(initial_num_infected/10)),
                                                                                params_to_change=params_to_change,
                                                                                interventions=intervention_scheme(compliance, ci_delay, hi_delay),
                                                                                datas_to_plot=datas_to_plot),
                                                                    num_repetitions=1))

    # add job to make r to base infectiousness graph:
    # jobs += [make_base_infectiousness_to_r_job('r_graph_default', city_name, scale,
    #                                            [0.03, 0.06, 0.1, 0.13, 0.16, 0.2],
    #                                            interventions=ci_sde,num_repetitions=3)]

    # this start the run of the jobs
    run(jobs, multi_processed=True, with_population_caching=False,verbosity=False)


if __name__ == "__main__":
    main()
