import math
import os
import statistics
import sys
from collections import namedtuple
from typing import List

import pandas
from functional import seq, pipeline
from matplotlib import pyplot

# can draw either bars or boxplot
draw_bar = True
draw_points_on_graph = False


class Categories:
    def __init__(self, one_run):
        parameters = one_run.split(',')
        self.city = parameters[0]
        self.intervention = parameters[1]
        if "ASCENDING" in one_run:
            self.order = "ASCENDING"
        elif "DESCENDING" in one_run:
            self.order = "DESCENDING"
        else:
            self.order = "NONE"
        if "HOUSEHOLDS_ALL_AT_ONCE" in one_run:
            self.vaccination_strategy = "HH_ALL_AT_ONCE"
        elif "HOUSEHOLD" in one_run:
            self.vaccination_strategy = "HOUSEHOLD"
        elif "BY_NEIGHBORHOOD" in one_run:
            self.vaccination_strategy = "BY_NEIGHBORHOOD"
        elif "GENERAL" in one_run:
            self.vaccination_strategy = "GENERAL"
        else:
            print(f"ERROR! unknown order! in {one_run}")
            exit(-1)
        self.immune_per_day = 0
        self.initial_infected = 0
        for i in range(len(parameters)):
            if 'imm_per_day' in parameters[i]:
                self.immune_per_day = parameters[i].split('=')[1]
            if 'inf=' in parameters[i]:
                self.initial_infected = parameters[i].split('=')[1]
            if 'comp=' in parameters[i]:
                self.compliance = parameters[i].split('=')[1]

    def __str__(self):
        return f"{self.city}\nINF={self.initial_infected}\nIMMUNE={self.immune_per_day}\n" \
               f"{self.vaccination_strategy}\n{self.order}\ncompliance={self.compliance}"


def sort_runs(a, b):
    return short_name(a) > short_name(b)


def short_name(a):
    return str(Categories(a))


def get_run_folders(root_dir):
    all_runs = [x for x in os.listdir(root_dir) if x[0] != "." and "csv" not in x and "svg" not in x]
    all_runs = seq(all_runs).sorted(short_name).list()
    return all_runs


def find_file_containing(root_dir, containing_string):
    file_name = [x for x in os.listdir(root_dir) if containing_string in x and "csv" in x]
    return file_name[0]


def get_sample_line(root_path, sample, amit_graph_type, line_name, as_is=False):
    filename = f"{root_path}/sample_{sample}/amit_graph_{amit_graph_type}.csv"
    if os.path.isfile(filename):
        data = seq.csv(filename)
        line = [i for i in range(data.len()) if data[i][0] == line_name][0]
        print(f'get_sample_line() of {amit_graph_type}, sample {sample}, line start with {data[line][0]}')
        if as_is:
            return [float(x) for x in data[line][1:]]
        else:
            return [max(0, float(x)) for x in data[line][1:]]
    return None


def get_daily_column(root_path, sample, column_name):
    filename = f"{root_path}/sample_{sample}/daily_delta.csv"
    if os.path.isfile(filename):
        data: pipeline.Sequence = seq.csv(filename)
        column = [i for i in range(data[0].len()) if data[0][i] == column_name][0]
        print(f'get_daily_column() of sample {sample}, line start with {data[0][column]}')
        return [max(0, float(x[column])) for x in data[1:]]
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


DAILY_INFO = namedtuple("DAILY_INFO", ("number_of_samples", "daily_infection",
                                       "infected_sum_mean", "infected_sum_stdev", "infected_sum",
                                       "critical_sum_mean", "critical_sum_stdev", "critical_sum",
                                       "infected_max_mean", "infected_max_stdev", "infected_max",
                                       "critical_max_mean", "critical_max_stdev", "critical_max"))


def stderr(data):
    return statistics.stdev(data) / math.sqrt(len(data))


def get_daily_info(root_path) -> DAILY_INFO:
    infected_sum = []
    max_infectious_in_community = []

    number_of_samples = 0
    daily_infection = None

    for i in range(1000):
        # infected_today = get_sample_line(root_path, i, "integral", 1)
        # critical_today = get_daily_column(root_path, sample=i, column=9)
        # if infected_today is not None and critical_today is not None:
        #     infected_sum.append(sum(critical_today))
        #     max_infectious_in_community.append(max(infected_today))
        #     number_of_samples += 1
        # else:
        #     break

        infected_today = get_daily_column(root_path, sample=i, column_name="infected_today")
        total_infected_in_community = get_sample_line(root_path, i, "integral", line_name="infected_0_99")

        if infected_today is not None and total_infected_in_community is not None:
            infected_sum.append(sum(infected_today))
            if daily_infection is None:
                daily_infection = seq(infected_today)
            else:
                daily_infection = daily_infection.zip(seq(infected_today)).map(lambda x: x[0] + x[1])
            max_infectious_in_community.append(max(total_infected_in_community))
            number_of_samples += 1
        else:
            break

    daily_infection = daily_infection.map(lambda x: x/number_of_samples)

    critical_sum = []
    critical_max = []

    for i in range(1000):
        critical_today = get_daily_column(root_path, sample=i, column_name="CRITICAL")
        total_critical_in_community = get_sample_line(root_path, sample=i, amit_graph_type="integral",
                                                      line_name="critical_0_99")

        if critical_today is not None and total_critical_in_community is not None:
            critical_sum.append(sum(critical_today))
            critical_max.append(max(total_critical_in_community))
        else:
            break

    # infected_sum_no_outliers, infected_sum_outliers = remove_outliers(infected_sum, method="percentile")
    # critical_sum_no_outliers, critical_sum_outliers = remove_outliers(critical_sum, method="percentile")
    # infected_max_no_outliers, infected_max_outliers = remove_outliers(max_infectious_in_community, method="percentile")
    # critical_max_no_outliers, critical_max_outliers = remove_outliers(critical_max, method="percentile")

    return DAILY_INFO(
        number_of_samples=number_of_samples,
        daily_infection=daily_infection.to_list(),
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
        critical_max_stdev=stderr(critical_max)
    )


def select_daily_graph_colors(vaccination_strategy, vaccination_order):
    colors = ['hotpink', 'lightskyblue', 'mediumpurple', 'mediumturquoise', 'darkorange']
    lines = [(0, (5, 10)), (0, (1, 1)), (0, (5, 1)), (0, (3, 1, 1, 1, 1, 1)), (0, (10, 0))]

    if vaccination_order == "DESCENDING":
        line_color = colors[0]
    else:
        line_color = colors[1]

    if vaccination_strategy == "GENERAL":
        line_pattern = lines[0]
    elif vaccination_strategy == "BY_NEIGHBORHOOD":
        line_pattern = lines[1]
    else:
        line_pattern = lines[2]

    line_label = f"{vaccination_strategy} - {vaccination_order}"

    return line_color, line_pattern, line_label


def draw_daily_graphs(df, ax):
    for key, daily_results in enumerate(df["daily_infection"]):
        color, line_style, label = select_daily_graph_colors(df["vaccination_strategy"].to_list()[key],
                                                             df["order"].to_list()[key])
        ax.plot(range(len(daily_results)), daily_results, label=label,
                              color=color,
                              linestyle=line_style)
        ax.legend()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("ERROR! please provide one argument which is the date/time of the run")
        exit(-1)

    all_runs = get_run_folders(f"../outputs/{sys.argv[1]}")
    df = pandas.DataFrame(columns=["scenario", "city", "initial_infected", "immune_per_day",
                                   "immune_order", "total_infected", "std_infected", "total_critical", "std_critical",
                                   "max_infevcted", "std_max_infected", "max_critical", "std_max_critical"])
    last_number_of_samples = None
    for one_run in all_runs:
        # daily_csv_filename = find_file_containing(f"../outputs/{sys.argv[1]}/{one_run}", "amit_graph_daily")
        # daily_integral_filename = find_file_containing(f"../outputs/{sys.argv[1]}/{one_run}", "amit_graph_integral")

        daily = get_daily_info(f"../outputs/{sys.argv[1]}/{one_run}")
        if last_number_of_samples is None:
            last_number_of_samples = daily.number_of_samples
        if last_number_of_samples != daily.number_of_samples:
            print(f"ERROR!! ERROR!! INCONSISTENT NUMBER OF SAMPLES!!! last_number_of_samples={last_number_of_samples} "
                  f"while current number of samples = {daily.number_of_samples}")
            exit(-2)
        c = Categories(one_run)
        df = df.append({"scenario": one_run,
                        "city": c.city,
                        "intervention": c.intervention,
                        "initial_infected": c.initial_infected,
                        "immune_per_day": c.immune_per_day,
                        "immune_order": str(c),
                        "compliance": c.compliance,
                        "vaccination_strategy": c.vaccination_strategy,
                        "order": c.order,

                        "daily_infection": daily.daily_infection,
                        "total_infected": daily.infected_sum_mean,
                        "std_infected": daily.infected_sum_stdev,
                        "infected_sum": daily.infected_sum,

                        "total_critical": daily.critical_sum_mean,
                        "std_critical": daily.critical_sum_stdev,
                        "critical_sum": daily.critical_sum,

                        "max_infected": daily.infected_max_mean,
                        "std_max_infected": daily.infected_max_stdev,
                        "infected_max": daily.infected_max,

                        "max_critical": daily.critical_max_mean,
                        "std_max_critical": daily.critical_max_stdev,
                        "critical_max": daily.critical_max
                        },
                       ignore_index=True)

        # daily_integral = seq.csv(f"../outputs/{sys.argv[1]}/{one_run}/{daily_integral_filename}")
        # infected = [float(x) for x in daily_integral[1][1:]]
        # max_infected = max(infected)
        # index_of_max_infected = infected.index(max_infected)
        # std_infected = daily_integral[3][1:][index_of_max_infected]

    df.to_csv(f"../outputs/{sys.argv[1]}/results.csv")

    categories = df.groupby(by=["city", "intervention", "initial_infected", "immune_per_day", "compliance"])

    fig, axs = pyplot.subplots(len(categories) * 4, 1)
    fig.set_figwidth(16)
    fig.set_figheight(len(categories) * 20)

    fig2, axs2 = pyplot.subplots(len(categories) * 4, 1)
    fig2.set_figwidth(16)
    fig2.set_figheight(len(categories) * 20)

    [ax.tick_params(axis='x', labelsize=6) for ax in axs]
    [ax.tick_params(axis='y', labelsize=6) for ax in axs]

    category_i = 0
    daily_category_i = 0
    for category in categories:
        print("\n\n")
        title = f'{category[0][0]}: intervention={category[0][1]}, initial={category[0][2]}, per-day={category[0][3]}, compliance={category[0][4]}'
        df = category[1]

        print(f"{category[1].scenario}")

        # plot a separator line between each category
        axs[category_i].plot([-1, 1.5], [1.3, 1.3], color='palevioletred', lw=3, transform=axs[category_i].transAxes,
                             clip_on=False)

        if draw_bar:
            axs[category_i].bar(df["immune_order"], df["total_infected"], color="lightsteelblue")
            axs[category_i].errorbar(df["immune_order"], df["total_infected"], yerr=df["std_infected"], capsize=10,
                                     ecolor="cornflowerblue", fmt=".")
            if draw_points_on_graph:
                axs[category_i].plot(df["immune_order"], df["infected_sum"].to_list(), "o")
        else:
            axs[category_i].boxplot(df["infected_sum"], labels=df["immune_order"])

        draw_daily_graphs(df, axs2[daily_category_i])
        axs2[daily_category_i].set_title(f"Daily Infected ({title})")
        daily_category_i += 1

        axs[category_i].set_title(f"Total Infected ({title})")
        category_i += 1

        if draw_bar:
            axs[category_i].bar(df["immune_order"], df["total_critical"], color="thistle")
            axs[category_i].errorbar(df["immune_order"], df["total_critical"], yerr=df["std_critical"], capsize=10,
                                     ecolor="slateblue", fmt=".")
            if draw_points_on_graph:
                axs[category_i].plot(df["immune_order"], df["critical_sum"].to_list(), "o")
        else:
            axs[category_i].boxplot(df["critical_sum"], labels=df["immune_order"])

        axs[category_i].set_title(f"Total Critical ({title})")
        category_i += 1

        if draw_bar:
            axs[category_i].bar(df["immune_order"], df["max_infected"], color="lightsteelblue")
            axs[category_i].errorbar(df["immune_order"], df["max_infected"], yerr=df["std_max_infected"], capsize=10,
                                     ecolor="cornflowerblue", fmt=".")
            if draw_points_on_graph:
                axs[category_i].plot(df["immune_order"], df["infected_max"].to_list(), "o")
        else:
            axs[category_i].boxplot(df["infected_max"], labels=df["immune_order"])

        axs[category_i].set_title(f"Max Infected ({title})")
        category_i += 1

        if draw_bar:
            axs[category_i].bar(df["immune_order"], df["max_critical"], color="thistle")
            axs[category_i].errorbar(df["immune_order"], df["max_critical"], yerr=df["std_max_critical"], capsize=10,
                                     ecolor="slateblue", fmt=".")
            if draw_points_on_graph:
                axs[category_i].plot(df["immune_order"], df["critical_max"].to_list(), "o")
        else:
            axs[category_i].boxplot(df["critical_max"], labels=df["immune_order"])

        axs[category_i].set_title(f"Max Critical ({title})")

        category_i += 1

    fig.suptitle(f'Analysis of simulation {sys.argv[1]}', fontsize=16)

    fig.tight_layout(pad=7.0)
    fig.savefig(f"../outputs/{sys.argv[1]}/results.svg")

    fig2.tight_layout(pad=7.0)
    fig2.savefig(f"../outputs/{sys.argv[1]}/daily_results.svg")
