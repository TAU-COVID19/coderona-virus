import json
from enum import Enum
import sys
import numpy as np
import pandas
from matplotlib import pyplot

from src.w import W
from src.simulation.params import Params
from categories import Categories


class GraphType(Enum):
    BAR = 1
    BOX = 2
    VIOLIN = 3


# can draw either bars or boxplot
selected_graph_type: GraphType = GraphType.VIOLIN
draw_points_on_graph = False
w = None


def sort_runs(a, b):
    return short_name(a) > short_name(b)


def short_name(a):
    return str(Categories(a))


def get_run_folders(root_dir):
    folders = [x for x in os.listdir(root_dir) if x[0] != "." and "csv" not in x and "svg" not in x]
    folders = seq(folders).sorted(short_name).list()
    return folders


from daily_graphs import *
from daily_data import *


def set_axis_style(ax, labels):
    ax.xaxis.set_tick_params(direction='out')
    ax.xaxis.set_ticks_position('bottom')
    # tick_label = ax.set_ticklabels(labels)
    ax.xaxis.set_ticks(ticks=np.arange(1, len(labels) + 1))
    ax.xaxis.set_ticklabels(labels)
    ax.set_xlim(0.25, len(labels) + 0.75)
    # ax.set_xlabel('Sample name')


if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), "../config.json")
    root_path = os.path.join(os.path.dirname(__file__), "../../")
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        paramsDataPath = ConfigData['ParamsFilePath']
    Params.load_from(os.path.join(root_path, "src/" + paramsDataPath), override=True)
    w = W()

    if len(sys.argv) != 2:
        print("ERROR! please provide one argument which is the date/time of the run")
        exit(-1)

    # add
    all_runs = get_run_folders(f"{root_path}/outputs/{sys.argv[1]}")
    df = pandas.DataFrame(columns=["scenario", "city", "initial_infected", "immune_per_day",
                                   "immune_order", "compliance", "vaccination_strategy", "order",
                                   "daily_infection", "daily_infection_stderr",
                                   "daily_critical_cases", "daily_critical_stderr",
                                   "total_infected", "std_infected", "total_critical", "std_critical",
                                   "max_infected", "std_max_infected", "max_critical", "std_max_critical"])
    last_number_of_samples = None
    for one_run in all_runs:
        daily = get_daily_info(f"{root_path}/outputs/{sys.argv[1]}/{one_run}")
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
                        "daily_infection_stderr": daily.daily_infection_stderr,
                        "daily_critical_cases": daily.daily_critical_cases,
                        "daily_critical_stderr": daily.daily_critical_stderr,
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

    df.to_csv(f'{root_path}/outputs/{sys.argv[1]}/results.csv')

    categories = df.groupby(by=["city", "intervention", "initial_infected", "immune_per_day", "compliance"])

    fig, axs = pyplot.subplots(len(categories) * 4, 1)
    fig.set_figwidth(16)
    fig.set_figheight(len(categories) * 40)

    fig2, axs2 = pyplot.subplots(len(categories) * 4, 1)
    fig2.set_figwidth(16)
    fig2.set_figheight(len(categories) * 20)

    [ax.tick_params(axis='x', labelsize=6) for ax in axs]
    [ax.tick_params(axis='y', labelsize=6) for ax in axs]

    category_i = 0
    daily_category_i = 0
    for category in categories:
        print("\n\n")
        title = f'{category[0][0]}: intervention={category[0][1]}, initial={category[0][2]}, "' \
                f'f"per-day={category[0][3]}, compliance={category[0][4]}'
        df = category[1]

        print(f"{category[1].scenario}")

        # plot a separator line between each category
        axs[category_i].plot([-1, 1.5], [1.3, 1.3], color='palevioletred', lw=3, transform=axs[category_i].transAxes,
                             clip_on=False)

        if selected_graph_type == GraphType.BAR:
            axs[category_i].bar(df["immune_order"], df["total_infected"], color="lightsteelblue")
            axs[category_i].errorbar(df["immune_order"], df["total_infected"], yerr=df["std_infected"], capsize=10,
                                     ecolor="cornflowerblue", fmt=".")
            if draw_points_on_graph:
                axs[category_i].plot(df["immune_order"], df["infected_sum"].to_list(), "o")
        elif selected_graph_type == GraphType.BOX:
            axs[category_i].boxplot(df["infected_sum"], labels=df["immune_order"])
        else:
            axs[category_i].violinplot(df["infected_sum"], showmedians=True, showextrema=False,
                                       quantiles=[[0.25, 0.75]] * len(df["immune_order"]))
            set_axis_style(axs[category_i], df["immune_order"])

        draw_daily_graphs(df, axs2[daily_category_i], plot_infection_graph=True)
        axs2[daily_category_i].set_title(f"Daily Infected ({title})")
        daily_category_i += 1

        draw_daily_graphs(df, axs2[daily_category_i], plot_infection_graph=False)
        axs2[daily_category_i].set_title(f"Total Critical Cases ({title})")
        daily_category_i += 1

        draw_daily_r_graph(df, axs2[daily_category_i], w)
        axs2[daily_category_i].set_title(f"Daily Instantaneous R ({title})")
        daily_category_i += 1

        axs[category_i].set_title(f"Daily Infected ({title})")
        category_i += 1

        if selected_graph_type == GraphType.BAR:
            axs[category_i].bar(df["immune_order"], df["total_critical"], color="thistle")
            axs[category_i].errorbar(df["immune_order"], df["total_critical"], yerr=df["std_critical"], capsize=10,
                                     ecolor="slateblue", fmt=".")
            if draw_points_on_graph:
                axs[category_i].plot(df["immune_order"], df["critical_sum"].to_list(), "o")
        elif selected_graph_type == GraphType.BOX:
            axs[category_i].boxplot(df["critical_sum"], labels=df["immune_order"])
        else:
            parts = axs[category_i].violinplot(df["critical_sum"], showmedians=True, showextrema=False,
                                               quantiles=[[0.25, 0.75]] * len(df["immune_order"]))
            set_axis_style(axs[category_i], df["immune_order"])
            for pc in parts['bodies']:
                pc.set_facecolor('#D43F3A')
                pc.set_edgecolor('black')
                pc.set_alpha(1)

        axs[category_i].set_title(f"Total Critical ({title})")
        category_i += 1

        if selected_graph_type == GraphType.BAR:
            axs[category_i].bar(df["immune_order"], df["max_infected"], color="lightsteelblue")
            axs[category_i].errorbar(df["immune_order"], df["max_infected"], yerr=df["std_max_infected"], capsize=10,
                                     ecolor="cornflowerblue", fmt=".")
            if draw_points_on_graph:
                axs[category_i].plot(df["immune_order"], df["infected_max"].to_list(), "o")
        elif selected_graph_type == GraphType.BOX:
            axs[category_i].boxplot(df["infected_max"], labels=df["immune_order"])
        else:
            axs[category_i].violinplot(df["infected_max"], showmedians=True, showextrema=False,
                                       quantiles=[[0.25, 0.75]] * len(df["immune_order"]))
            set_axis_style(axs[category_i], df["immune_order"])

        axs[category_i].set_title(f"Max Infected ({title})")
        category_i += 1

        if selected_graph_type == GraphType.BAR:
            axs[category_i].bar(df["immune_order"], df["max_critical"], color="thistle")
            axs[category_i].errorbar(df["immune_order"], df["max_critical"], yerr=df["std_max_critical"], capsize=10,
                                     ecolor="slateblue", fmt=".")
            if draw_points_on_graph:
                axs[category_i].plot(df["immune_order"], df["critical_max"].to_list(), "o")
        elif selected_graph_type == GraphType.BOX:
            axs[category_i].boxplot(df["critical_max"], labels=df["immune_order"])
        else:
            axs[category_i].violinplot(df["critical_max"], showmedians=True, showextrema=False,
                                       quantiles=[[0.25, 0.75]] * len(df["immune_order"]))
            set_axis_style(axs[category_i], df["immune_order"])

        axs[category_i].set_title(f"Max Critical ({title})")

        category_i += 1

    fig.suptitle(f'Analysis of simulation {sys.argv[1]}', fontsize=16)

    fig.tight_layout(pad=7.0)
    fig.savefig(f"{root_path}/outputs/{sys.argv[1]}/results.svg")

    fig2.tight_layout(pad=7.0)
    fig2.savefig(f"{root_path}/outputs/{sys.argv[1]}/daily_results.svg")
