import math
import statistics
from functional import seq, pipeline
from collections import namedtuple
from typing import List
import os
import numpy as np


def get_sample_line(root_path, sample, amit_graph_type, line_name, as_is=False):
    filename = f"{root_path}/sample_{sample}/amit_graph_{amit_graph_type}.csv"
    if os.path.isfile(filename):
        data = seq.csv(filename)
        line = [i for i in range(data.len()) if data[i][0] == line_name][0]
        print(f'get_sample_line() of {amit_graph_type}, sample {sample}, line start with {data[line][0]}')
        if as_is:
            return [float(x) for x in data[line][1:]]
        else:
            return [max(0.0, float(x)) for x in data[line][1:]]
    return None


def get_daily_column(root_path, sample, column_name):
    filename = f"{root_path}/sample_{sample}/daily_delta.csv"
    if os.path.isfile(filename):
        data: pipeline.Sequence = seq.csv(filename)
        column = [i for i in range(data[0].len()) if data[0][i] == column_name][0]
        print(f'get_daily_column() of sample {sample}, line start with {data[0][column]}')
        return [max(0.0, float(x[column])) for x in data[1:]]
    return None


def remove_outliers(data: List[float], method="stdev"):
    if method == "stdev":
        data_mean, data_std = statistics.mean(data), statistics.stdev(data)
        # identify outliers
        cut_off = data_std * 3
        lower, upper = data_mean - cut_off, data_mean + cut_off
    else:  # use percentile
        from numpy import percentile
        q25, q75 = percentile(data, 25), percentile(data, 75)
        iqr = q75 - q25
        cut_off = iqr * 1.5
        lower, upper = q25 - cut_off, q75 + cut_off

    outliers_removed = [x for x in data if lower < x < upper]
    outliers = [x for x in data if x > upper or x < lower]
    return outliers_removed, outliers


DAILY_INFO = namedtuple("DAILY_INFO", ("number_of_samples", "daily_infection", "daily_critical_cases",
                                       "infected_sum_mean", "infected_sum_stdev", "infected_sum",
                                       "critical_sum_mean", "critical_sum_stdev", "critical_sum",
                                       "infected_max_mean", "infected_max_stdev", "infected_max",
                                       "critical_max_mean", "critical_max_stdev", "critical_max",
                                       "daily_infection_stderr", "daily_critical_stderr"))


def stderr(data):
    return statistics.stdev(data) / math.sqrt(len(data))


def get_daily_info(root_path) -> DAILY_INFO:
    infected_sum = []
    max_infectious_in_community = []

    number_of_samples = 0
    daily_infection = None
    daily_infection_full_data = None

    for i in range(1000):
        infected_today = get_daily_column(root_path, sample=i, column_name="infected_today")
        total_infected_in_community = get_sample_line(root_path, i, "integral", line_name="infected_0_99")

        if infected_today is not None and total_infected_in_community is not None:
            infected_sum.append(sum(infected_today))
            if daily_infection is None:
                daily_infection = seq(total_infected_in_community)
                daily_infection_full_data = np.array([total_infected_in_community])
            else:
                daily_infection = daily_infection.zip(seq(total_infected_in_community)).map(lambda x: x[0] + x[1])
                daily_infection_full_data = np.append(daily_infection_full_data, [total_infected_in_community], axis=0)
            max_infectious_in_community.append(max(total_infected_in_community))
            number_of_samples += 1
        else:
            break

    daily_infection = daily_infection.map(lambda x: x / number_of_samples)

    critical_sum = []
    critical_max = []
    daily_critical_cases = None
    daily_critical_full_data = None


    for i in range(1000):
        critical_today = get_daily_column(root_path, sample=i, column_name="CRITICAL")
        total_critical_in_community = get_sample_line(root_path, sample=i, amit_graph_type="integral",
                                                      line_name="critical_0_99")

        if critical_today is not None and total_critical_in_community is not None:
            critical_sum.append(sum(critical_today))
            critical_max.append(max(total_critical_in_community))
        else:
            break

        if daily_critical_cases is None:
            daily_critical_cases = seq(total_critical_in_community)
            daily_critical_full_data = np.array([total_critical_in_community])
        else:
            daily_critical_cases = daily_critical_cases.zip(seq(total_critical_in_community)).map(lambda x: x[0] + x[1])
            daily_critical_full_data = np.append(daily_critical_full_data, [total_critical_in_community], axis=0)

    daily_critical_cases = daily_critical_cases.map(lambda x: x / number_of_samples)

    # infected_sum_no_outliers, infected_sum_outliers = remove_outliers(infected_sum, method="percentile")
    # critical_sum_no_outliers, critical_sum_outliers = remove_outliers(critical_sum, method="percentile")
    # infected_max_no_outliers, infected_max_outliers = remove_outliers(max_infectious_in_community,method="percentile")
    # critical_max_no_outliers, critical_max_outliers = remove_outliers(critical_max, method="percentile")

    return DAILY_INFO(
        number_of_samples=number_of_samples,
        daily_infection=daily_infection.to_list(),
        daily_critical_cases=daily_critical_cases.to_list(),
        infected_sum=infected_sum,
        infected_sum_mean=statistics.mean(infected_sum),
        infected_sum_stdev=stderr(infected_sum),
        critical_sum=critical_sum,
        critical_sum_mean=statistics.mean(critical_sum),
        critical_sum_stdev=stderr(critical_sum),
        infected_max=max_infectious_in_community,
        infected_max_mean=statistics.mean(max_infectious_in_community),
        infected_max_stdev=stderr(max_infectious_in_community),
        critical_max=critical_max,
        critical_max_mean=statistics.mean(critical_max),
        critical_max_stdev=stderr(critical_max),
        daily_infection_stderr=np.apply_along_axis(stderr, 0, daily_infection_full_data).tolist(),
        daily_critical_stderr=np.apply_along_axis(stderr, 0, daily_critical_full_data).tolist()
    )
