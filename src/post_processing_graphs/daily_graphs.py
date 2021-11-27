from typing import List
from functional import seq


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


def draw_daily_graphs(df, ax, plot_infection_graph):
    if plot_infection_graph:
        for key, daily_results in enumerate(df["daily_infection"]):
            color, line_style, label = select_daily_graph_colors(df["vaccination_strategy"].to_list()[key],
                                                                 df["order"].to_list()[key])
            ax.plot(range(len(daily_results)), daily_results, label=label,
                    color=color,
                    linestyle=line_style)
            ax.legend()
    else:  # plot daily critical cases
        for key, daily_results in enumerate(df["daily_critical_cases"]):
            color, line_style, label = select_daily_graph_colors(df["vaccination_strategy"].to_list()[key],
                                                                 df["order"].to_list()[key])
            ax.plot(range(len(daily_results)), daily_results, label=label,
                    color=color,
                    linestyle=line_style)
            ax.legend()


def draw_daily_r_graph(df, ax, w):
    for key, daily_results in enumerate(df["daily_infection"]):
        r = calculate_r0_instantaneous(daily_results, w)
        color, line_style, label = select_daily_graph_colors(df["vaccination_strategy"].to_list()[key],
                                                             df["order"].to_list()[key])
        ax.plot(range(len(r)), r, label=label,
                color=color,
                linestyle=line_style)
        ax.legend()


def calculate_r0_instantaneous(infected_per_day: List[int], w) -> List[float]:
    """calculates the instantaneous r based on a look back of look_back_days days"""

    r = []

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