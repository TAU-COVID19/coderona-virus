from src.simulation.interventions import *
from src.run_utils import INITIAL_DATE
from datetime import date, timedelta
from src.seir import daysdelta
from src.world.environments.environment import EnvironmentalAttribute


def scenario_1_interventions(compliance, ci_delay, hi_delay):
    ci_intervention = SymptomaticIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay=ci_delay
    )
    sd_intervention = SocialDistancingIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        age_range=(0, 99)
    )
    school_closer_intervention = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=1.0,
        city_name='all',
        age_segment=(3, 22)
    )
    workplace_closure_intervention = WorkplaceClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=0.85
    )
    elderly_intervention = ElderlyQuarantineIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        min_age=70
    )
    household_intervention = HouseholdIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay_on_enter=hi_delay
    )
    interventions = [ci_intervention,
                      sd_intervention,
                      workplace_closure_intervention,
                      elderly_intervention,
                      household_intervention,
                      school_closer_intervention
                      ]
    return interventions

def scenario_21_interventions(compliance, ci_delay, hi_delay):
    ci_intervention = SymptomaticIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay=ci_delay
    )
    sd_intervention = SocialDistancingIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        age_range=(0, 99)
    )
    school_closer_intervention = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=0.98,
        city_name='all',
        age_segment=(3, 22)
    )
    workplace_closure_intervention = WorkplaceClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=0.7
    )
    elderly_intervention = ElderlyQuarantineIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        min_age=65
    )
    household_intervention = HouseholdIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay_on_enter=hi_delay
    )
    interventions = [ci_intervention,
                      sd_intervention,
                      workplace_closure_intervention,
                      elderly_intervention,
                      household_intervention,
                      school_closer_intervention
                      ]
    return interventions

def scenario_22_interventions(compliance, ci_delay, hi_delay):
    ci_intervention = SymptomaticIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay=ci_delay
    )
    sd_intervention = SocialDistancingIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        age_range=(0, 99)
    )
    school_closer_intervention = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=0.98,
        city_name='all',
        age_segment=(3, 17)
    )
    school_closer_intervention_yeshiva = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=0.5,
        city_name='all',
        age_segment=(18, 22)
    )
    school_isolation_intervention_yeshiva = SchoolIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=0.5,
        city_name='all',
        age_segment=(18, 22)
    )
    workplace_closure_intervention = WorkplaceClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=0.70
    )
    elderly_intervention = ElderlyQuarantineIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        min_age=65
    )
    household_intervention = HouseholdIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay_on_enter=hi_delay
    )
    interventions = [ci_intervention,
                      sd_intervention,
                      workplace_closure_intervention,
                      elderly_intervention,
                      household_intervention,
                      school_closer_intervention,
                      school_isolation_intervention_yeshiva,
                      school_closer_intervention_yeshiva
                      ]
    return interventions

def scenario_23_interventions(compliance, ci_delay, hi_delay):
    ci_intervention = SymptomaticIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay=ci_delay
    )
    sd_intervention = SocialDistancingIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        age_range=(0, 99)
    )
    school_closer_intervention = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=0.98,
        city_name='all',
        age_segment=(10, 22)
    )
    workplace_closure_intervention = WorkplaceClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=0.70
    )
    elderly_intervention = ElderlyQuarantineIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        min_age=65
    )
    household_intervention = HouseholdIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay_on_enter=hi_delay
    )
    interventions = [ci_intervention,
                      sd_intervention,
                      workplace_closure_intervention,
                      elderly_intervention,
                      household_intervention,
                      school_closer_intervention
                      ]
    return interventions

def scenario_24_interventions(compliance, ci_delay, hi_delay):
    ci_intervention = SymptomaticIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay=ci_delay
    )
    sd_intervention = SocialDistancingIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        age_range=(0, 99)
    )
    school_closer_intervention = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=0.98,
        city_name='all',
        age_segment=(10, 17)
    )
    school_closer_intervention_yeshiva = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=0.5,
        city_name='all',
        age_segment=(18, 22)
    )
    school_isolation_intervention_yeshiva = SchoolIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=0.5,
        city_name='all',
        age_segment=(18, 22)
    )
    workplace_closure_intervention = WorkplaceClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=0.70
    )
    elderly_intervention = ElderlyQuarantineIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        min_age=65
    )
    household_intervention = HouseholdIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay_on_enter=hi_delay
    )
    interventions = [ci_intervention,
                      sd_intervention,
                      workplace_closure_intervention,
                      elderly_intervention,
                      household_intervention,
                      school_closer_intervention,
                      school_closer_intervention_yeshiva,
                      school_isolation_intervention_yeshiva
                      ]
    return interventions

def scenario_25_interventions(compliance, ci_delay, hi_delay):
    ci_intervention = SymptomaticIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay=ci_delay
    )
    sd_intervention = SocialDistancingIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        age_range=(0, 99)
    )
    school_closer_intervention = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=0.98,
        city_name='all',
        age_segment=(6, 17)
    )
    school_closer_intervention_yeshiva = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=0.5,
        city_name='all',
        age_segment=(18, 22)
    )
    school_isolation_intervention_yeshiva = SchoolIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=0.5,
        city_name='all',
        age_segment=(18, 22)
    )
    workplace_closure_intervention = WorkplaceClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=0.70
    )
    elderly_intervention = ElderlyQuarantineIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        min_age=65
    )
    household_intervention = HouseholdIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay_on_enter=hi_delay
    )
    interventions = [ci_intervention,
                      sd_intervention,
                      workplace_closure_intervention,
                      elderly_intervention,
                      household_intervention,
                      school_closer_intervention,
                      school_closer_intervention_yeshiva,
                      school_isolation_intervention_yeshiva
                      ]
    return interventions

def scenario_26_interventions(compliance, ci_delay, hi_delay):
    ci_intervention = SymptomaticIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay=ci_delay
    )
    sd_intervention = SocialDistancingIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        age_range=(0, 99)
    )
    periodic_school_closure_intervention = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=1.0,
        city_name='all',
        age_segment=(3, 9),
        period_data=AttributeAndPeriodData(
            EnvironmentalAttribute('household', 'last name', 2),
            timedelta(7)
        )
    )
    school_closer_intervention = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=0.98,

        city_name='all',
        age_segment=(10, 22)
    )
    workplace_closure_intervention = WorkplaceClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=0.70
    )
    elderly_intervention = ElderlyQuarantineIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        min_age=65
    )
    household_intervention = HouseholdIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay_on_enter=hi_delay
    )
    interventions = [ci_intervention,
                     sd_intervention,
                     workplace_closure_intervention,
                     elderly_intervention,
                     household_intervention,
                     school_closer_intervention,
                     periodic_school_closure_intervention
                     ]
    return interventions


def scenario_232_interventions(compliance, ci_delay, hi_delay):
    ci_intervention = SymptomaticIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay=ci_delay
    )
    sd_intervention = SocialDistancingIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        age_range=(0, 99)
    )
    school_closer_intervention = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=0.98,
        city_name='all',
        age_segment=(10, 22)
    )
    workplace_closure_intervention = WorkplaceClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=0.70
    )
    elderly_intervention = ElderlyQuarantineIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        min_age=65
    )
    household_intervention = HouseholdIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay_on_enter=hi_delay
    )
    interventions = [ci_intervention,
                     sd_intervention,
                     workplace_closure_intervention,
                     elderly_intervention,
                     household_intervention,
                     school_closer_intervention
                     ]
    return interventions


def scenario_262_interventions(compliance, ci_delay, hi_delay):
    ci_intervention = SymptomaticIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay=ci_delay
    )
    sd_intervention = SocialDistancingIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        age_range=(0, 99)
    )
    periodic_school_closure_intervention = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=1.0,
        city_name='all',
        age_segment=(3, 9),
        period_data=AttributeAndPeriodData(
            EnvironmentalAttribute('household', 'last name', 2),
            timedelta(7)
        )
    )
    school_closer_intervention = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=0.98,
        city_name='all',
        age_segment=(10, 22)
    )
    workplace_closure_intervention = WorkplaceClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=0.70
    )
    elderly_intervention = ElderlyQuarantineIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        min_age=65
    )
    household_intervention = HouseholdIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay_on_enter=hi_delay
    )
    interventions = [ci_intervention,
                     sd_intervention,
                     workplace_closure_intervention,
                     elderly_intervention,
                     household_intervention,
                     school_closer_intervention,
                     periodic_school_closure_intervention
                     ]
    return interventions


def scenario_272_interventions(compliance, ci_delay, hi_delay):
    ci_intervention = SymptomaticIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay=ci_delay
    )
    sd_intervention = SocialDistancingIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        age_range=(0, 99)
    )
    periodic_school_closure_intervention = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=1.0,
        city_name='all',
        age_segment=(3, 6),
        period_data=AttributeAndPeriodData(
            EnvironmentalAttribute('household', 'last name', 2),
            timedelta(7)
        )
    )
    school_closer_intervention = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=0.98,
        city_name='all',
        age_segment=(7, 22)
    )
    workplace_closure_intervention = WorkplaceClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=0.70
    )
    elderly_intervention = ElderlyQuarantineIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        min_age=65
    )
    household_intervention = HouseholdIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay_on_enter=hi_delay
    )
    interventions = [ci_intervention,
                     sd_intervention,
                     workplace_closure_intervention,
                     elderly_intervention,
                     household_intervention,
                     school_closer_intervention,
                     periodic_school_closure_intervention
                     ]
    return interventions


def scenario_282_interventions(compliance, ci_delay, hi_delay):
    ci_intervention = SymptomaticIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay=ci_delay
    )
    sd_intervention = SocialDistancingIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        age_range=(0, 99)
    )
    school_closer_intervention = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=0.98,
        city_name='all',
        age_segment=(7, 22)
    )
    workplace_closure_intervention = WorkplaceClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=0.70
    )
    elderly_intervention = ElderlyQuarantineIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        min_age=65
    )
    household_intervention = HouseholdIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay_on_enter=hi_delay
    )
    interventions = [ci_intervention,
                     sd_intervention,
                     workplace_closure_intervention,
                     elderly_intervention,
                     household_intervention,
                     school_closer_intervention
                     ]
    return interventions


#scenarios 36, 39, 365, 395

def scenario_36_interventions(compliance, ci_delay, hi_delay):
    ci_intervention = SymptomaticIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay=ci_delay
    )
    sd_intervention = SocialDistancingIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        age_range=(0, 99)
    )
    school_closer_intervention = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=0.98,
        city_name='all',
        age_segment=(7, 22)
    )
    workplace_closure_intervention = WorkplaceClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=0.70
    )
    elderly_intervention = ElderlyQuarantineIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        min_age=65
    )
    household_intervention = HouseholdIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay_on_enter=hi_delay
    )
    interventions = [ci_intervention,
                     sd_intervention,
                     workplace_closure_intervention,
                     elderly_intervention,
                     household_intervention,
                     school_closer_intervention
                     ]
    return interventions

def scenario_39_interventions(compliance, ci_delay, hi_delay):
    ci_intervention = SymptomaticIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay=ci_delay
    )
    sd_intervention = SocialDistancingIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        age_range=(0, 99)
    )
    school_closer_intervention = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=0.98,
        city_name='all',
        age_segment=(10, 22)
    )
    workplace_closure_intervention = WorkplaceClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=0.70
    )
    elderly_intervention = ElderlyQuarantineIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        min_age=65
    )
    household_intervention = HouseholdIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay_on_enter=hi_delay
    )
    interventions = [ci_intervention,
                     sd_intervention,
                     workplace_closure_intervention,
                     elderly_intervention,
                     household_intervention,
                     school_closer_intervention
                     ]
    return interventions


def scenario_365_interventions(compliance, ci_delay, hi_delay):
    ci_intervention = SymptomaticIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay=ci_delay
    )
    sd_intervention = SocialDistancingIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        age_range=(0, 99)
    )
    periodic_school_closure_intervention = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=1.0,
        city_name='all',
        age_segment=(3, 6),
        period_data=AttributeAndPeriodData(
            EnvironmentalAttribute('household', 'last name', 2),
            timedelta(7)
        )
    )
    school_closer_intervention = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=0.98,
        city_name='all',
        age_segment=(7, 22)
    )
    workplace_closure_intervention = WorkplaceClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=0.70
    )
    elderly_intervention = ElderlyQuarantineIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        min_age=65
    )
    household_intervention = HouseholdIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay_on_enter=hi_delay
    )
    interventions = [ci_intervention,
                     sd_intervention,
                     workplace_closure_intervention,
                     elderly_intervention,
                     household_intervention,
                     school_closer_intervention,
                     periodic_school_closure_intervention
                     ]
    return interventions


def scenario_395_interventions(compliance, ci_delay, hi_delay):
    ci_intervention = SymptomaticIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay=ci_delay
    )
    sd_intervention = SocialDistancingIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        age_range=(0, 99)
    )
    periodic_school_closure_intervention = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=1.0,
        city_name='all',
        age_segment=(3, 9),
        period_data=AttributeAndPeriodData(
            EnvironmentalAttribute('household', 'last name', 2),
            timedelta(7)
        )
    )
    school_closer_intervention = SchoolClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=1.0,
        proportion_of_envs=0.98,
        city_name='all',
        age_segment=(10, 22)
    )
    workplace_closure_intervention = WorkplaceClosureIntervention(
        start_date=INITIAL_DATE,
        duration=daysdelta(60),
        compliance=0.70
    )
    elderly_intervention = ElderlyQuarantineIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        min_age=65
    )
    household_intervention = HouseholdIsolationIntervention(
        start_date=INITIAL_DATE,
        duration=timedelta(60),
        compliance=compliance,
        delay_on_enter=hi_delay
    )
    interventions = [ci_intervention,
                     sd_intervention,
                     workplace_closure_intervention,
                     elderly_intervention,
                     household_intervention,
                     school_closer_intervention,
                     periodic_school_closure_intervention
                     ]
    return interventions




