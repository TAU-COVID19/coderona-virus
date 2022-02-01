from typing import List

import pandas
import seaborn
from functional import seq
import numpy as np


def select_daily_graph_colors(vaccination_strategy, vaccination_order):
    colors = ['hotpink', 'lightskyblue', 'mediumpurple', 'mediumturquoise', 'darkorange']
    lines = [(0, (5, 0)), (0, (1, 1)), (0, (8, 8)), (0, (5, 1)), (0, (3, 1, 1, 1, 1, 1)), (0, (10, 0))]

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


def draw_daily_graphs(df, ax, plot_infection_graph):
    if plot_infection_graph:
        for key, daily_results in enumerate(df["infected_cumulative_mean"]):
            std_err = df["infected_cumulative_stdev"].tolist()[key]
            color, line_style, label = select_daily_graph_colors(df["vaccination_strategy"].to_list()[key],
                                                                 df["order"].to_list()[key])
            ax.plot(range(len(daily_results)), daily_results, label=label,
                    color=color,
                    linestyle=line_style)
            # draw the confidence interval
            lower_range = (np.array(daily_results) - np.array(std_err)).tolist()
            upper_range = (np.array(daily_results) + np.array(std_err)).tolist()
            ax.fill_between(range(len(daily_results)), lower_range, upper_range, color=color, alpha=.1)
            ax.set_xlim(0, len(daily_results))
            ax.legend(prop={"size": 8})
    else:  # plot daily critical cases
        for key, daily_results in enumerate(df["critical_cumulative_mean"]):
            std_err = df["critical_cumulative_stdev"].tolist()[key]
            color, line_style, label = select_daily_graph_colors(df["vaccination_strategy"].to_list()[key],
                                                                 df["order"].to_list()[key])
            ax.plot(range(len(daily_results)), daily_results, label=label,
                    color=color,
                    linestyle=line_style)
            # draw the confidence interval
            lower_range = (np.array(daily_results) - np.array(std_err)).tolist()
            upper_range = (np.array(daily_results) + np.array(std_err)).tolist()
            ax.fill_between(range(len(daily_results)), lower_range, upper_range, color=color, alpha=.1)
            ax.set_xlim(0, len(daily_results))
            ax.legend(prop={"size": 8})


def draw_heatmap(ax, categories: pandas.DataFrame, for_total_infections: bool = True):
    number_of_categories = categories.__len__()
    number_of_strategies = categories.head(2)["vaccination_strategy"].count()
    d = np.ndarray(shape=(number_of_categories, number_of_strategies), dtype=float)
    for category in categories:
        df = category[1]
        data = np.array(df["total_infected_in_the_community"])[:][-1]
        for key, r_case_reproduction_number in enumerate(df["total_infected_in_the_community"]):
            pass
        seaborn.set_theme()
        x = range(len(df["vaccination_strategy"].to_list()))
        seaborn.heatmap()
        ax.legend(prop={"size": 8})


def draw_daily_r_graph_2(ax, df, use_r_instantaneous):
    for key, r_case_reproduction_number in enumerate(df["r_case_reproduction_number"]):
        r_instantaneous = df["r_instantaneous"].to_list()[key]
        if r_instantaneous is None:
            return
        color, line_style, label = select_daily_graph_colors(df["vaccination_strategy"].to_list()[key],
                                                             df["order"].to_list()[key])

        if use_r_instantaneous:
            x = range(8, len(r_instantaneous))
            ax.plot(x, r_instantaneous[8:], label=label,
                    color=color,
                    linestyle=line_style)
            ax.set_xlim(min(x), max(x))
        else:
            x = range(0, len(r_case_reproduction_number))
            ax.plot(x, r_case_reproduction_number, label=label,
                    color=color,
                    linestyle=line_style)
        ax.plot(x, [1] * len(x), color="lightgreen")
        ax.set_xlim(min(x), max(x))
        ax.legend(prop={"size": 8})


def draw_daily_r_graph(df, ax, w):
    for key, daily_results in enumerate(df["daily_infection"]):
        r = calculate_r0_instantaneous(daily_results, w)
        r_avg = moving_average(r, 7)
        color, line_style, label = select_daily_graph_colors(df["vaccination_strategy"].to_list()[key],
                                                             df["order"].to_list()[key])
        # ax.plot(range(8, len(r)), r[8:], label=label,
        #         color=color,
        #         linestyle=line_style)
        x = range(8, len(r_avg))
        ax.plot(x, r_avg[8:], label=label,
                color=color,
                linestyle=line_style)
        ax.plot(x, [1] * len(x), color="lightgreen")

        # ax.fill_between(range(8, len(r_avg)), 0.8, 1, color="#069c1d", alpha=.1)
        # ax.fill_between(range(8, len(r_avg)), 1, 1.5, color="#990800", alpha=.1)
        ax.legend(prop={"size": 8})


def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w


def calculate_r0_instantaneous(infected_per_day: List[int], w) -> List[float]:
    """calculates the instantaneous r based on a look back of look_back_days days"""

    r = []
    look_back_days = 0
    for i in range(len(infected_per_day)):
        look_back_days = w.w_len()
        if i <= look_back_days:
            r.append(0)
        else:
            r_today = infected_per_day[i] \
                      / max(seq([w.get_w(look_back) *
                                 infected_per_day[i - look_back]
                                 for look_back in range(1, look_back_days)]).sum(), 1)
            r.append(r_today)

    return r
