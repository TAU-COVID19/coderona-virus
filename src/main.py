import logging
import json
import numpy as np
import os
from datetime import date, timedelta
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.world.environments import EnvironmentalAttribute
#from src.simulation.interventions import *
from src.seir import daysdelta
from src.scenarios import *
from src.seir import DiseaseState
from src.simulation.initial_infection_params import NaiveInitialInfectionParams, SmartInitialInfectionParams
from src.logs import make_age_and_state_datas_to_plot
from src.simulation.params import Params

from src.run_utils import RepeatJob, SimpleJob, run, INITIAL_DATE
import src.util.seed as seed

seed.set_random_seed()

log = logging.getLogger(__name__)

"""
# examples of initializing different interventions

# case isolation - isolating to quarantine mode every person that develops symptoms
ci_intervention = SymptomaticIsolationIntervention(
    start_date=INITIAL_DATE,
    duration=daysdelta(500),
    compliance=0.7,
    delay=0
)



# house isolation - isolate the entire house when one of them develops symptoms
# here it's configures for 14 days from symptoms
hq_intervention = HouseholdIsolationIntervention(
    start_date=INITIAL_DATE + daysdelta(15),
    duration=daysdelta(120),
    compliance=0.7,
    delay_on_enter=0,
    delay_on_exit=14,
    is_exit_after_recovery=False
)

# social distancing - decrease contacts outside of household (mainly) for the given duration
sd_intervention = SocialDistancingIntervention(
    start_date=INITIAL_DATE + daysdelta(15),
    duration=daysdelta(120),
    compliance=0.75,
    age_range=(5, 10)
)

# school isolation - simulates kids staying at school and not returning
# here, it's configured for the entire country
school_isolation_intervention = SchoolIsolationIntervention(
    start_date=INITIAL_DATE + daysdelta(0),
    duration=daysdelta(120),
    compliance=0.7,
    proportion_of_envs=0.35,
    city_name='all',
    age_segment=(5, 12)
)

# workplace closure - close all working places
workplace_closure_intervention = WorkplaceClosureIntervention(
    start_date=INITIAL_DATE + daysdelta(10),
    duration=daysdelta(120),
    compliance=1.0
)

# distance all the elder people, here it's configured from age 70 and up
elderly_intervention = ElderlyQuarantineIntervention(
    start_date=INITIAL_DATE + daysdelta(30),
    duration=daysdelta(120),
    compliance=0.75,
    min_age=70
)

# simulates the closure of Jerusalem - no one is getting in or out for the duration that is given
jerusalem_intervention = CityCurfewIntervention(
    'jerusalem',
    start_date=INITIAL_DATE,
    duration=daysdelta(120),
    compliance=0.7
)

# simulates the closure of Tel Aviv - no one is getting in or out for the duration that is given
tlv_intervention = CityCurfewIntervention(
    'tel aviv-yafo',
    start_date=INITIAL_DATE,
    duration=daysdelta(120),
    compliance=0.7
)

# school closer - the kids in the given age range do not go to school
school_closure_intervention = SchoolClosureIntervention(
    start_date=INITIAL_DATE,
    duration=daysdelta(120),
    compliance=1.0,
    proportion_of_envs=1.0,
    city_name='all',
    age_segment=(3, 18)
)

# simulates a two week cycle in which every week, one half of the kids (by household) go to school
periodic_school_closure_intervention = SchoolClosureIntervention(
    start_date=INITIAL_DATE,
    duration=daysdelta(120),
    compliance=1.0,
    proportion_of_envs=1.0,
    city_name='all',
    age_segment=(3, 18),
    period_data=AttributeAndPeriodData(
        EnvironmentalAttribute('household', 'last name', 2),
        timedelta(7)
    )
)

# simulates a three week cycle in which every week, one third of the kids (by household) go to school
periodic_school_closure_intervention_2 = SchoolClosureIntervention(
    start_date=INITIAL_DATE,
    duration=daysdelta(120),
    compliance=1.0,
    proportion_of_envs=1.0,
    city_name='all',
    age_segment=(3, 18),
    period_data=AttributeAndPeriodData(
        EnvironmentalAttribute('household', 'last name', 3),
        timedelta(7)
    )
)

# examples of different scenarios of intervention together

# only case isolation
ci = [ci_intervention]

# case isolation and school closure
ci_pc = [ci_intervention, sd_intervention]

# case isolation ans workplace closure
ci_wc = [
    ci_intervention,
    workplace_closure_intervention
]

# Case Isolation and Household Quarantine
ci_hq = [ci_intervention, hq_intervention]

# School closing
# pc = [school_closure_intervention]

# CI, HQ, Elderly Quarantine
ci_sde = [
    ci_intervention,
    hq_intervention,
    elderly_intervention,
]

# CI, HQ, SD for entire population
ci_hq_sd = [
    ci_intervention,
    hq_intervention,
    sd_intervention
]

# Closing Schools, CI, SD for entire population
ci_pc_sd = [
    ci_intervention,
    sd_intervention,
    school_closure_intervention
]

# closing schools periodically (two weeks cycle), social distancing and case isolation
ci_sd_psc = [
    ci_intervention,
    sd_intervention,
    periodic_school_closure_intervention
]

# closing schools periodically (three weeks cycle), social distancing and case isolation
ci_sd_psc2 = [
    ci_intervention,
    sd_intervention,
    periodic_school_closure_intervention_2
]

# closing schools, isolating kids at school, social distancing and case isolation
ci_pc_pi_sd = [
    ci_intervention,
    sd_intervention,
    school_closure_intervention,
    school_isolation_intervention
]

# closing schools, isolating kids at school, work closure, social distancing and case isolation
ci_pc_pi_sd_wc = [
    ci_intervention,
    sd_intervention,
    school_closure_intervention,
    school_isolation_intervention,
    workplace_closure_intervention
]

# closure of Tel Aviv and Jerusalen with case isolation
city_cerfew = [
    ci_intervention,
    jerusalem_intervention,
    tlv_intervention
]
"""


def generate_scenario_name(city_name, scenario, initial_num_infected,initial_per_immuned, compliance, ci_delay, hi_delay, symptomatic_probs_scale):
    return f"{city_name}_{scenario}_init_{initial_num_infected}_immune_percenage_{initial_per_immuned}_comp_{compliance}_cidelay_{ci_delay}_hidelay_{hi_delay}_symsc_{symptomatic_probs_scale}"
    
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
        ]
    }
    return {'amit_graph': make_age_and_state_datas_to_plot(
        age_groups=((0, 19), (20, 59), (60, 99)),
        disease_state_groups=list(graphs.items())
    )}

def main():
    """
    This is the main function that runs the simulation.
    here we are able to add different intervention, params, and more configurations to the run.
    This is an example for using the code in the project, and running different simulations of the disease.
    """
    # sets the logging output to be at debug level, meaning more output than a regular run
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    """
    # all interventions to activate, all the uncommented line will be added as a different simulation run
    # the keys are the names of the run, and the values are the list of active interventions in the run
    interventions_modes = {
        'default': [],
        'CI': ci,
        # 'CI_SDE': ci_sde,
        'CI_PC': ci_pc,
        'CI_PC_SD': ci_pc_sd,
        'CI_PC_HSD': ci_sd_psc,
        'CI_PC_HSD2': ci_sd_psc2
        # 'CI_PC_PI_SD': ci_pc_pi_sd,
        # 'CI_WC': ci_wc,
        # 'CI_PC_PI_SD_WC': ci_pc_pi_sd_wc
        # 'CI': ci,
        # 'CI_SDE': ci_sde,
        # 'CI_PC_SD': ci_pc_sd,
        # 'CI_PC_PI_SD_WC': ci_pc_pi_sd_wc,
        # 'CC': city_cerfew
        # 'CI_HQ': ci_hq,
        # 'PC': pc,
        # 'CI_HQ_SD': ci_hq_sd,
    }
    """
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
        "paper_8": paper_8
        #"paper_2_comp_9": paper_2_comp_9
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
    for initial_percentage_immune in [0.0,0.5]:
        for initial_num_infected in [25, 100, 250, 500]:
            for city_name, scale in [("Holon",1), ("Bene Beraq",1)]:
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
                                                                                    compliance,
                                                                                    ci_delay,
                                                                                    hi_delay,
                                                                                    symptomatic_probs_scale)
    #                                    full_scenario_name = "res"
                                        jobs.append(RepeatJob(SimpleJob(full_scenario_name,
                                                                        days=180,
                                                                        city_name=city_name,
                                                                        scale=scale,
                                                                        infection_params=NaiveInitialInfectionParams(initial_num_infected,per_to_Immune=initial_percentage_immune),
                                                                        #infection_params=SmartInitialInfectionParams(initial_num_infected, round(initial_num_infected/10)),
                                                                        params_to_change=params_to_change,
                                                                        interventions=intervention_scheme(compliance, ci_delay, hi_delay),
                                                                        datas_to_plot=datas_to_plot),
                                                            num_repetitions=50))

    # add job to make r to base infectiousness graph:
    # jobs += [make_base_infectiousness_to_r_job('r_graph_default', city_name, scale,
    #                                            [0.03, 0.06, 0.1, 0.13, 0.16, 0.2],
    #                                            interventions=ci_sde,num_repetitions=3)]

    # this start the run of the jobs
    run(jobs, multi_processed=True, with_population_caching=False,verbosity=False)


if __name__ == "__main__":
    main()
