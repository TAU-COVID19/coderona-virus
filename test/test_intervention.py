from datetime import timedelta
import os
import pytest

from src.run_utils import SimpleJob, run, INITIAL_DATE
from src.simulation.interventions import *
from src.simulation.initial_infection_params import SmartInitialInfectionParams
from src.logs import Statistics


@pytest.fixture(params=[False, True])
def hi_exit(request, params):
    """
    This fixture creates params for HouseholdIsolationIntervention.
    Returns params that makes sure the household stays at home until the symptomatic people are immune.
    :param request: states the is_after value
    :param params: simulation params
    :return: (delay_on_exit, is_exit_after_recovery) params for intervention
    """
    is_after = request.param
    if is_after:
        return (1, True)
    else:
        disease_params = params['disease_parameters']
        delay_on_exit = 1
        for param in disease_params.values():
            if 'max_val' in param:
                delay_on_exit += param['max_val']
        return (delay_on_exit, False)


def test_household_isolation_intervention_simulation(hi_exit):
    """
    Tests that when asymptomatic and presymptomatic people are not infectious and household isolation occur with no delay,
    all the poeple that are infected are infected at home (of at the beginning), due to the household isolation
    :param hi_exit: params that make sure there are no delay or too short of isolation
    :return: None (since this is a test), but it is asserted that all infections occur within the household
    """
    scenario_name = "test_HI"
    params_to_change = {
        ("disease_parameters", "infectiousness_per_stage", "incubating_post_latent"): 0.0,
        ("disease_parameters", "infectiousness_per_stage", "asymptomatic"): 0.0
    }
    delay_on_exit, is_exit_after_recovery = hi_exit
    job = SimpleJob(scenario_name, city_name='kefar yona', interventions=[
        HouseholdIsolationIntervention(
            compliance=1,
            start_date=INITIAL_DATE, duration=timedelta(250),
            delay_on_enter=0, delay_on_exit=delay_on_exit,
            is_exit_after_recovery=is_exit_after_recovery
        )
    ], scale=1.0, params_to_change=params_to_change, infection_params=SmartInitialInfectionParams(100, 50))
    outdir = run([job], multi_processed=False, with_population_caching=False)
    results = Statistics.load(os.path.join(outdir, scenario_name, 'statistics.pkl'))
    summary = results.get_summary_data_for_age_group((0, 99))
    assert summary["Total infected in household"] + summary["Total infected in initial_group"] == summary[
        "Total infected"]


def test_school_closure_intervention_simulation():
    """
    Test that when school isolation is on, no one is infected at school.
    :return: True is there are 0 infections at school
    """
    scenario_name = "test_PC"
    job = SimpleJob(scenario_name, city_name='kefar yona', interventions=[
        SchoolClosureIntervention(
            start_date=INITIAL_DATE,
            duration=timedelta(250),
            compliance=1.0,
            proportion_of_envs=1.0,
            city_name='kefar yona',
            age_segment=(0, 9)
        )
    ], scale=1.0, infection_params=SmartInitialInfectionParams(100, 50))
    outdir = run([job], multi_processed=False, with_population_caching=False)
    results = Statistics.load(os.path.join(outdir, scenario_name, 'statistics.pkl'))
    summary = results.get_summary_data_for_age_group((0, 9))
    assert summary["Total infected in school"] == 0


def test_school_isolation_intervention_simulation():
    """
    Test that when school isolation is on, all the relevant people are infected only at shool
    """
    scenario_name = "test_PI"
    job = SimpleJob(scenario_name, city_name='kefar yona', interventions=[
        SchoolIsolationIntervention(
            start_date=INITIAL_DATE,
            duration=timedelta(250),
            compliance=1.0,
            proportion_of_envs=1.0,
            city_name='kefar yona',
            age_segment=(4, 12)
        )
    ], scale=1.0, infection_params=SmartInitialInfectionParams(100, 50))
    outdir = run([job], multi_processed=False, with_population_caching=False)
    results = Statistics.load(os.path.join(outdir, scenario_name, 'statistics.pkl'))
    summary = results.get_summary_data_for_age_group((4, 12))
    assert summary["Total infected in school"] + summary["Total infected in initial_group"] == summary["Total infected"]
