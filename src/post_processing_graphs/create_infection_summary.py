import json
import sys
from enum import Enum

import pandas
import scipy.stats
import seaborn
from matplotlib import pyplot

from categories import Categories
from src.simulation.params import Params
from src.w import W


class GraphType(Enum):
    BAR = 1
    BOX = 2
    VIOLIN = 3


# set to True to show the different cities in different graphs. else set to False
including_city = True
# can draw either bars or boxplot
selected_graph_type: GraphType = GraphType.VIOLIN
draw_points_on_graph = False
# max number of days to process
max_number_of_days_to_graph = 150
# you can limit the number of iterations we process (for quicker testing only). set to None for normal operation
debug_max_iterations = None



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


def plot_wilcoxon_ranksum_statistic(ax, data_per_strategy: pandas.DataFrame, strategies: pandas.DataFrame, title: str):
    results = []
    labels = []
    for key_row, series_row in enumerate(data_per_strategy):
        row = []
        labels = []
        for key_column, series_column in enumerate(data_per_strategy):
            statistic, p_value = scipy.stats.ranksums(x=series_row, y=series_column, alternative='two-sided')
            row.append(f'{p_value:.3f}')
            this_label = strategies[strategies.index[key_column]]
            labels.append(this_label)
        results.append(row)

    the_table = ax.table(cellText=results, rowLabels=labels, colLabels=labels, loc='center', cellLoc='center')
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.set_axis_off()
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(8)
    table_props = the_table.properties()
    table_cells = table_props['children']
    for cell in table_cells:
        cell.set_width(0.2)
        cell.set_height(0.15)
    # the_table.scale(1.5, 1.5)
    ax.set_title(f'Wilcoxon Rank-Sum P Value - {title}')


def set_axis_style(ax, labels):
    ax.xaxis.set_tick_params(direction='out')
    ax.xaxis.set_ticks_position('bottom')
    # tick_label = ax.set_ticklabels(labels)
    ax.xaxis.set_ticks(ticks=np.arange(1, len(labels) + 1))
    ax.xaxis.set_ticklabels(labels)
    ax.set_xlim(0.25, len(labels) + 0.75)
    # ax.set_xlabel('Sample name')


def prepare_seaborn_df(data, categories):
    d = pandas.DataFrame(columns=["strategy", "data"])
    for key, results in enumerate(data):
        d = pandas.concat([d, pandas.DataFrame(data=[[categories[categories.index[key]], i] for i in results],
                                               columns=["strategy", "data"])])
    return d


def draw_violin_graph(ax, x, data):
    def adjacent_values(vals, q1, q3):
        upper_adjacent_value = q3 + (q3 - q1) * 1.5
        upper_adjacent_value = np.clip(upper_adjacent_value, q3, vals[-1])

        lower_adjacent_value = q1 - (q3 - q1) * 1.5
        lower_adjacent_value = np.clip(lower_adjacent_value, vals[0], q1)
        return lower_adjacent_value, upper_adjacent_value

    ax.grid(True)
    ax.tick_params(axis='both', which='major', labelsize=8)
    # set the min Violin Y value to show to be 0
    ax.set_ylim(bottom=0, top=max([max(x) for x in data]))
    colors = ['darkorchid','plum', 'darkorchid','plum']
    seaborn.set_palette(seaborn.color_palette(colors))
    seaborn_df = prepare_seaborn_df(data, x)
    v = seaborn.violinplot(x="strategy", y="data", data=seaborn_df, linewidth=1.0,  ax=ax)
    for violin, alpha in zip(ax.collections[::2], [0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8]):
        violin.set_alpha(alpha)
    v.set_xlabel("Strategy", fontsize=18)
    v.set_ylabel("", fontsize=18)
    return


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
                                   "critical_cumulative", "critical_cumulative_mean", 'critical_cumulative_stdev',
                                   "max_infected", "std_max_infected", "max_critical", "std_max_critical"])
    last_number_of_samples = None
    for one_run in all_runs:
        daily = get_daily_info(f"{root_path}/outputs/{sys.argv[1]}/{one_run}", max_days=max_number_of_days_to_graph,
                               max_iterations=debug_max_iterations)
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

                        "total_hospitalized_mean": daily.total_hospitalized_mean,
                        "total_hospitalized_stderr": daily.total_hospitalized_stderr,

                        "total_infected_in_the_community": daily.total_infected_in_the_community,
                        "total_infected_in_the_community_stderr": daily.total_infected_in_the_community_stderr,

                        "total_critical_in_the_community": daily.total_critical_in_the_community,
                        "total_critical_in_the_community_stderr": daily.total_critical_in_the_community_stderr,

                        "daily_critical_cases": daily.daily_critical_cases,
                        "daily_critical_stderr": daily.daily_critical_stderr,
                        "infected_cumulative_mean": daily.infected_cumulative_mean,
                        "infected_cumulative_stdev": daily.infected_cumulative_stdev,

                        "critical_cumulative_mean": daily.critical_cumulative_mean,
                        "critical_cumulative_stdev": daily.critical_cumulative_stdev,

                        "max_infected": daily.infected_max_mean,
                        "std_max_infected": daily.infected_max_stdev,
                        "infected_max": daily.infected_max,

                        "max_critical": daily.critical_max_mean,
                        "std_max_critical": daily.critical_max_stdev,
                        "critical_max": daily.critical_max,
                        "r_instantaneous": daily.r_instantaneous,
                        "r_case_reproduction_number": daily.r_case_reproduction_number
                        },
                       ignore_index=True)

    df.to_csv(f'{root_path}/outputs/{sys.argv[1]}/results.csv')

    if including_city:
        category_items = ["city", "intervention", "initial_infected", "immune_per_day", "compliance"]
    else:
        category_items = ["intervention", "initial_infected", "immune_per_day", "compliance"]

    categories = df.groupby(by=category_items)

    # define the properties of the Violin graphs
    fig, axs = pyplot.subplots(len(categories) * 5, 1)
    fig.set_figwidth(25)
    fig.set_figheight(len(categories) * 30)

    # define the properties of the daily graphs
    fig2, axs2 = pyplot.subplots(20, 1)
    fig2.set_figwidth(9)
    fig2.set_figheight(len(categories) * 24)

    [ax.tick_params(axis='x', labelsize=6) for ax in axs]
    [ax.tick_params(axis='y', labelsize=6) for ax in axs]

    category_i = 0
    daily_category_i = 0
    for category in categories:
        city = f'{category[0][category_items.index("city")]}: ' if "city" in category_items else ''
        title = city +\
                f'intervention={category[0][category_items.index("intervention")]}, ' \
                f'initial={category[0][category_items.index("initial_infected")]}, '\
                f'per-day={category[0][category_items.index("immune_per_day")]}, '\
                f'compliance={category[0][category_items.index("compliance")]}'
        df = category[1]

        # # plot a separator line between each category
        # axs[category_i].plot([-1, 1.5], [1.3, 1.3], color='palevioletred', lw=3, transform=axs[category_i].transAxes,
        #                      clip_on=False)

        if selected_graph_type == GraphType.BAR:
            axs[category_i].bar(df["immune_order"], df["total_infected_in_the_community"], color="lightsteelblue")
            axs[category_i].errorbar(df["immune_order"], df["total_infected_in_the_community"],
                                     yerr=df["total_infected_in_the_community_stderr"],
                                     capsize=10,
                                     ecolor="cornflowerblue", fmt=".")
            if draw_points_on_graph:
                axs[category_i].plot(df["immune_order"], df["total_infected_in_the_community"].to_list(), "o")
        elif selected_graph_type == GraphType.BOX:
            axs[category_i].boxplot(df["total_infected_in_the_community"], labels=df["immune_order"])
        else:
            draw_violin_graph(ax=axs[category_i], x=df["immune_order"], data=df["total_infected_in_the_community"])

        axs[category_i].set_title(f"Total Infected\n{title}")
        category_i += 1

        draw_violin_graph(ax=axs[category_i], x=df["immune_order"], data=df["total_hospitalized_mean"])
        axs[category_i].set_title(f"Total Hospitalization\n{title}")
        category_i += 1

        draw_daily_graphs(df, axs2[daily_category_i], graph_type=DailyGraphType.INFECTED)
        axs2[daily_category_i].set_title(f"Infected Cumulative Sum \n({title})")
        axs2[daily_category_i].set_xlabel("Day")
        daily_category_i += 1

        draw_daily_graphs(df, axs2[daily_category_i], graph_type=DailyGraphType.CRITICAL)
        axs2[daily_category_i].set_title(f"Critical Cumulative Sum \n({title})")
        axs2[daily_category_i].set_xlabel("Day")
        daily_category_i += 1

        draw_daily_graphs(df, axs2[daily_category_i], graph_type=DailyGraphType.HOSPITALISED)
        axs2[daily_category_i].set_title(f"Hospitalised Cumulative Sum \n({title})")
        axs2[daily_category_i].set_xlabel("Day")
        daily_category_i += 1

        # draw_daily_r_graph(df, axs2[daily_category_i], w)
        draw_daily_r_graph_2(axs2[daily_category_i], df, use_r_instantaneous=True)
        axs2[daily_category_i].set_title(f"Instantaneous R \n({title})")
        axs2[daily_category_i].set_xlabel("Day")
        daily_category_i += 1

        draw_daily_r_graph_2(axs2[daily_category_i], df, use_r_instantaneous=False)
        axs2[daily_category_i].set_title(f"Case Reproduction Number R \n({title})")
        axs2[daily_category_i].set_xlabel("Day")
        daily_category_i += 1

        plot_wilcoxon_ranksum_statistic(ax=axs[category_i],
                                        data_per_strategy=df["total_infected_in_the_community"],
                                        strategies=df["immune_order"],
                                        title='Total Infected')
        category_i += 1

        if selected_graph_type == GraphType.BAR:
            axs[category_i].bar(df["immune_order"], df["total_critical_in_the_community"], color="thistle")
            axs[category_i].errorbar(df["immune_order"], df["total_critical_in_the_community"],
                                     yerr=df["total_critical_in_the_community_stderr"], capsize=10,
                                     ecolor="slateblue", fmt=".")
            if draw_points_on_graph:
                axs[category_i].plot(df["immune_order"], df["total_critical_in_the_community"].to_list(), "o")
        elif selected_graph_type == GraphType.BOX:
            axs[category_i].boxplot(df["total_critical_in_the_community"], labels=df["immune_order"])
        else:
            draw_violin_graph(ax=axs[category_i], x=df["immune_order"], data=df["total_critical_in_the_community"])

        axs[category_i].set_title(f"Total Critical\n{title}")
        category_i += 1

        plot_wilcoxon_ranksum_statistic(ax=axs[category_i],
                                        data_per_strategy=df["total_critical_in_the_community"],
                                        strategies=df["immune_order"],
                                        title='Total Critical')
        category_i += 1

        # if selected_graph_type == GraphType.BAR:
        #     axs[category_i].bar(df["immune_order"], df["max_infected"], color="lightsteelblue")
        #     axs[category_i].errorbar(df["immune_order"], df["max_infected"], yerr=df["std_max_infected"], capsize=10,
        #                              ecolor="cornflowerblue", fmt=".")
        #     if draw_points_on_graph:
        #         axs[category_i].plot(df["immune_order"], df["infected_max"].to_list(), "o")
        # elif selected_graph_type == GraphType.BOX:
        #     axs[category_i].boxplot(df["infected_max"], labels=df["immune_order"])
        # else:
        #     draw_violin_graph(ax=axs[category_i], x=df["immune_order"], data=df["infected_max"])
        #
        # axs[category_i].set_title(f"Max Infected ({title})")
        # category_i += 1
        #
        # if selected_graph_type == GraphType.BAR:
        #     axs[category_i].bar(df["immune_order"], df["max_critical"], color="thistle")
        #     axs[category_i].errorbar(df["immune_order"], df["max_critical"], yerr=df["std_max_critical"], capsize=10,
        #                              ecolor="slateblue", fmt=".")
        #     if draw_points_on_graph:
        #         axs[category_i].plot(df["immune_order"], df["critical_max"].to_list(), "o")
        # elif selected_graph_type == GraphType.BOX:
        #     axs[category_i].boxplot(df["critical_max"], labels=df["immune_order"])
        # else:
        #     draw_violin_graph(ax=axs[category_i], x=df["immune_order"], data=df["critical_max"])
        #
        # axs[category_i].set_title(f"Max Critical ({title})")
        #
        # category_i += 1

    # draw_heatmap(axs2[daily_category_i], categories, for_total_infections=True)


    fig.suptitle(f'Analysis of simulation {sys.argv[1]}', fontsize=16)

    fig.tight_layout(pad=15.0)
    fig.savefig(f"{root_path}/outputs/{sys.argv[1]}/results.svg")

    fig2.tight_layout(pad=7.0)
    fig2.savefig(f"{root_path}/outputs/{sys.argv[1]}/daily_results.svg")
