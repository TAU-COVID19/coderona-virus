import pandas as pd
from scipy.interpolate import interp1d
import numpy as np
from src.seir.disease_state import DiseaseState
import datetime

def symptomatic_interpolation(seir_times):
    '''
    a function that gets a symptomatic's person disease course and returns its TP probability for each day of the disease course
    input: SEIR times in the format of dictionary
    output: TP probability values for each day of the disease
    '''

    # loading data from table
    df = pd.read_excel(r'/mnt/c/Users/achiy/Desktop/Distribution.xlsx')
    x_latent = df["Days since exposure"][df["Phase"] == 'latent'].values
    x_pre = df["Days since exposure"][df["Phase"] == 'pre-symptomatic'].values
    x_symp = df["Days since exposure"][df["Phase"] == 'symptomatic'].values

    y_latent = df["TP"][df["Phase"] == 'latent'].values
    y_pre = df["TP"][df["Phase"] == 'pre-symptomatic'].values
    y_symp = df["TP"][df["Phase"] == 'symptomatic'].values

    # the interpolation itself
    f_latent = interp1d(x_latent, y_latent, kind='linear')
    f_pre = interp1d(x_pre, y_pre, kind='linear')
    f_symp = interp1d(x_symp, y_symp, kind='linear')

    example_latent_period = np.linspace(min(x_latent), max(x_latent), seir_times[DiseaseState.LATENT])
    example_pre_period = np.linspace(min(x_pre), max(x_pre), seir_times[DiseaseState.INCUBATINGPOSTLATENT])
    example_symp_period = np.linspace(min(x_symp), max(x_symp), seir_times[DiseaseState.SYMPTOMATICINFECTIOUS])

    example_latent_tp_rate = f_latent(example_latent_period)
    example_pre_tp_rate = f_pre(example_pre_period)
    example_symp_tp_rate = f_symp(example_symp_period)

    tp_values_example = np.concatenate(
        [example_latent_tp_rate, example_pre_tp_rate, example_symp_tp_rate])

    return tp_values_example

def asymptomatic_interpolation(seir_times):
    '''
    a function that gets an asymptomatic's person disease course and returns its TP probability for each day of the disease course
    input: SEIR times in the format of dictionary
    output: TP probability values for each day of the disease
    '''

    df = pd.read_excel(r'/mnt/c/Users/achiy/Desktop/AsymDistribution.xlsx')
    x_latent = df["Days since exposure"][df["Phase"] == 'LATENT'].values
    x_infection = df["Days since exposure"][df["Phase"] == 'ASYMPTOMATICINFECTIOUS'].values

    y_latent = df["AsyTP"][df["Phase"] == 'LATENT'].values
    y_infection = df["AsyTP"][df["Phase"] == 'ASYMPTOMATICINFECTIOUS'].values

    f_latent = interp1d(x_latent, y_latent, kind='linear')
    f_infection = interp1d(x_infection, y_infection, kind='linear')

    example_latent_period = np.linspace(min(x_latent), max(x_latent), seir_times[DiseaseState.LATENT])
    example_infection_period = np.linspace(min(x_infection), max(x_infection), seir_times[DiseaseState.ASYMPTOMATICINFECTIOUS])

    example_latent_tp_rate = f_latent(example_latent_period)
    example_infection_tp_rate = f_infection(example_infection_period)

    tp_values_example = np.concatenate(
        [example_latent_tp_rate, example_infection_tp_rate])

    return tp_values_example

def get_interpolation_format(seir_times):
    '''
    a function that changes the format of the SEIR times given by the simulation
    input: the output of the simulation to the following code: sim._world.person.get_person_from_id().seir_times
    output: the same data in the format of a dictionary
    '''

    critical_idx = -1
    for i in range(len(seir_times)):
        if seir_times[i][0] == DiseaseState.CRITICAL:
            critical_idx = i
            for j in range(len(seir_times)):
                if seir_times[j][0] == DiseaseState.SYMPTOMATICINFECTIOUS:
                    seir_times[j] = (DiseaseState.SYMPTOMATICINFECTIOUS, seir_times[j][1] + seir_times[i][1])
                    break
            break
    if critical_idx != -1:
        seir_times.pop(critical_idx)

    interpolation_format = {}
    for i in range(len(seir_times)):
        interpolation_format[seir_times[i][0]] = seir_times[i][1].days
    return interpolation_format

if __name__ == '__main__':

    seir_times_sim_format = [
        (DiseaseState.LATENT, datetime.timedelta(days=6)),
        (DiseaseState.INCUBATINGPOSTLATENT, datetime.timedelta(days=2)),
        (DiseaseState.SYMPTOMATICINFECTIOUS, datetime.timedelta(days=3)),
        # (DiseaseState.CRITICAL, datetime.timedelta(days=7)),
        (DiseaseState.IMMUNE, datetime.timedelta(days=3))
    ]

    example = get_interpolation_format(seir_times_sim_format)

    # # sanity check values: [3, 2, 17, 10]
    # example_seir_times = [2, 2, 17, 10]
    example_seir_times = {
        DiseaseState.LATENT: 3,
        DiseaseState.INCUBATINGPOSTLATENT: 2,
        DiseaseState.SYMPTOMATICINFECTIOUS: 27,
        DiseaseState.IMMUNE: 10
    }

    tp_rates_example = symptomatic_interpolation(example_seir_times)
    print('for disease ' + str(example_seir_times) + ' we got the tp rates: ' + str(tp_rates_example))

    # # sanity check values: [5, 16]
    # example_seir_times_asymp = {
    #     DiseaseState.LATENT: 5,
    #     DiseaseState.ASYMPTOMATICINFECTIOUS: 16
    # }
    # tp_rates_example = asymptomatic_interpolation(example_seir_times_asymp)
    # print('for disease ' + str(example_seir_times_asymp) + ' we got the tp rates: ' + str(tp_rates_example))

    #

