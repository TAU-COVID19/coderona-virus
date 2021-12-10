import math
import os
import statistics
from collections import namedtuple
from typing import List

import numpy as np
from functional import seq, pipeline


def get_sample_line(root_path, sample, amit_graph_type, line_name, as_is=False):
    filename = f"{root_path}/sample_{sample}/amit_graph_{amit_graph_type}.csv"
    if os.path.isfile(filename):
        data = seq.csv(filename)
        line = [i for i in range(data.len()) if data[i][0] == line_name][0]
        # print(f'get_sample_line() of {amit_graph_type}, sample {sample}, line start with {data[line][0]}')
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
        # print(f'get_daily_column() of sample {sample}, line start with {data[0][column]}')
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


DAILY_INFO = namedtuple("DAILY_INFO", ("number_of_samples",
                                       "daily_infection",
                                       "daily_critical_cases",
                                       "total_infected_in_the_community", "total_infected_in_the_community_stderr",
                                       "total_critical_in_the_community", "total_critical_in_the_community_stderr",
                                       "infected_cumulative_mean", "infected_cumulative_stdev",
                                       "critical_cumulative_mean", "critical_cumulative_stdev",
                                       "infected_max_mean", "infected_max_stdev", "infected_max",
                                       "critical_max_mean", "critical_max_stdev", "critical_max",
                                       "daily_infection_stderr", "daily_critical_stderr"))


def stderr(data):
    return statistics.stdev(data) / math.sqrt(len(data))


def cumulative_sum(data):
    return np.cumsum(data)


def get_daily_info(root_path) -> DAILY_INFO:
    infected_cumulative = []
    max_infectious_in_community = []

    number_of_repetitions = 0
    daily_infection = None
    daily_infection_full_data = None
    total_infected_in_community = None

    for i in range(1000):
        infected_today = get_daily_column(root_path, sample=i, column_name="infected_today")
        total_infected_today = get_sample_line(root_path, i, "integral", line_name="infected_0_99")

        if infected_today is not None and total_infected_today is not None:
            if daily_infection is None:
                daily_infection = seq(infected_today)
                daily_infection_full_data = np.array([infected_today])
                infected_cumulative = np.array([cumulative_sum(infected_today)])
                total_infected_in_community = np.array([total_infected_today])
            else:
                daily_infection = daily_infection.zip(seq(infected_today)).map(lambda x: x[0] + x[1])
                daily_infection_full_data = np.append(daily_infection_full_data, [infected_today], axis=0)
                infected_cumulative = np.append(infected_cumulative, [cumulative_sum([infected_today])], axis=0)
                total_infected_in_community = np.append(total_infected_in_community, [total_infected_today], axis=0)
            max_infectious_in_community.append(max(total_infected_today))
            number_of_repetitions += 1
        else:
            break

    daily_infection = daily_infection.map(lambda x: x / number_of_repetitions)

    critical_cumulative = None
    critical_max = []
    daily_critical_cases = None
    daily_critical_full_data = None
    total_critical_in_community = None

    for i in range(1000):
        critical_today = get_daily_column(root_path, sample=i, column_name="CRITICAL")
        total_critical_today = get_sample_line(root_path, sample=i, amit_graph_type="integral",
                                               line_name="critical_0_99")

        if critical_today is not None and total_critical_today is not None:
            if total_critical_in_community is None:
                critical_cumulative = np.array([cumulative_sum(critical_today)])
                total_critical_in_community = np.array([total_critical_today])
            else:
                critical_cumulative = np.append(critical_cumulative, [cumulative_sum([critical_today])], axis=0)
                total_critical_in_community = np.append(total_critical_in_community,
                                                        [total_critical_today], axis=0)
            critical_max.append(max(total_critical_today))
        else:
            break

        if daily_critical_cases is None:
            daily_critical_cases = seq(critical_today)
            daily_critical_full_data = np.array([critical_today])
        else:
            daily_critical_cases = daily_critical_cases.zip(seq(critical_today)).map(lambda x: x[0] + x[1])
            daily_critical_full_data = np.append(daily_critical_full_data, [critical_today], axis=0)

    daily_critical_cases = daily_critical_cases.map(lambda x: x / number_of_repetitions)

    # infected_sum_no_outliers, infected_sum_outliers = remove_outliers(infected_cumulative, method="percentile")
    # critical_sum_no_outliers, critical_sum_outliers = remove_outliers(critical_cumulative, method="percentile")
    # infected_max_no_outliers, infected_max_outliers = remove_outliers(max_infectious_in_community,method="percentile")
    # critical_max_no_outliers, critical_max_outliers = remove_outliers(critical_max, method="percentile")

    return DAILY_INFO(
        number_of_samples=number_of_repetitions,
        daily_infection=daily_infection.to_list(),
        daily_critical_cases=daily_critical_cases.to_list(),

        total_infected_in_the_community=total_infected_in_community.mean(axis=0).tolist(),
        total_infected_in_the_community_stderr=(
                total_infected_in_community.std(axis=0) / math.sqrt(number_of_repetitions)).tolist(),

        total_critical_in_the_community=total_critical_in_community.mean(axis=0).tolist(),
        total_critical_in_the_community_stderr=(
                total_critical_in_community.std(axis=0) / math.sqrt(number_of_repetitions)).tolist(),

        infected_cumulative_mean=infected_cumulative.mean(axis=0).tolist(),
        infected_cumulative_stdev=(infected_cumulative.std(axis=0) / math.sqrt(number_of_repetitions)).tolist(),

        critical_cumulative_mean=critical_cumulative.mean(axis=0).tolist(),
        critical_cumulative_stdev=(critical_cumulative.std(axis=0) / math.sqrt(number_of_repetitions)).tolist(),

        infected_max=max_infectious_in_community,
        infected_max_mean=statistics.mean(max_infectious_in_community),
        infected_max_stdev=stderr(max_infectious_in_community),
        critical_max=critical_max,
        critical_max_mean=statistics.mean(critical_max),
        critical_max_stdev=stderr(critical_max),
        daily_infection_stderr=np.apply_along_axis(stderr, 0, daily_infection_full_data).tolist(),
        daily_critical_stderr=np.apply_along_axis(stderr, 0, daily_critical_full_data).tolist()
    )
