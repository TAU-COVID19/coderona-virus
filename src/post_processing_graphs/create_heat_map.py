import sys

from matplotlib import pyplot
import seaborn as sns
import pandas as pd


def draw_heatmap(ax, df: pd.DataFrame):
    sns.set_theme()
    sns.set(font_scale=1.4)
    sns.heatmap(data=df, ax=ax, cmap="Spectral_r", annot=True, fmt=",.0f")

    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontsize(16)
    # ax.legend()


if __name__ == "__main__":
    plots = 8
    fig, ax = pyplot.subplots(plots, 1)
    fig.set_figwidth(22)
    fig.set_figheight(plots * 10)

    # ----------- FILL HERE THE REAL DATA ------------

    # ----------- START ------------
    total_infections_hh_isolation = [
        (8138, 8743, 7586, 7579),  # Bnei Brak
        (2226, 4424, 2063, 2726)]  # Holon

    total_critical_hh_isolation = [
        (1579, 304, 724, 481),  # Bnei Brak
        (1134, 831, 888, 770)]  # Holon

    # List of tuples
    total_infections_asymptomatic_detection = [
        (1289, 1518, 1157, 1188),  # Bnei Brak
        (899, 1609, 896, 1102)]  # Holon

    total_critical_asymptomatic_detection = [
        (349, 183, 231, 212),  # Bnei Brak
        (574, 551, 537, 492)]  # Holon

    # some up the cities
    # hh combinations:
    #   neighborhood_descending_bnei_brak + neighborhood_ascending_holon
    #   general_descending_bnei_brak + neighborhood_descending_holon
    # asymptomatic combinations:
    #   general_descending_bnei_brak + neighborhood_descending_holon
    total_infection_hh_both_cities_detection = [
        total_infections_hh_isolation[0][i] + total_infections_hh_isolation[1][i] for i in range(4)] + [7579+2063, 8743+2726]
    total_infections_asymptomatic_both_cities_detection = [
        total_infections_asymptomatic_detection[0][i] + total_infections_asymptomatic_detection[1][i] for i in range(4)] + [1518+1102]

    # hh combinations:
    #   neighborhood_descending_bnei_brak + neighborhood_ascending_holon
    #   general_descending_bnei_brak + neighborhood_descending_holon
    # asymptomatic combinations:
    #   general_descending_bnei_brak + neighborhood_descending_holon
    total_critical_hh_both_cities_detection = [
        total_critical_hh_isolation[0][i] + total_critical_hh_isolation[1][i] for i in range(4)] + [481+888, 304+770]
    total_critical_asymptomatic_both_cities_detection = [
        total_critical_asymptomatic_detection[0][i] + total_critical_asymptomatic_detection[1][i] for i in range(4)] + [183+492]
    # ----------- END ------------

    df = pd.DataFrame(total_infections_hh_isolation,
                      columns=[
                          'General\nAscending',
                          'General\nDescending',
                          'Neighborhood\nAscending',
                          'Neighborhood\nDescending',
                      ],
                      index=['Bnei Brak', 'Holon'])
    draw_heatmap(ax[0], df)
    ax[0].set_title(f"Total Infection for - Household Isolation")

    df = pd.DataFrame(total_critical_hh_isolation,
                      columns=[
                          'General\nAscending',
                          'General\nDescending',
                          'Neighborhood\nAscending',
                          'Neighborhood\nDescending',
                      ],
                      index=['Bnei Brak', 'Holon'])
    draw_heatmap(ax[1], df)
    ax[1].set_title(f"Total Critical for - Household Isolation")

    df = pd.DataFrame(total_infections_asymptomatic_detection,
                      columns=[
                          'General\nAscending',
                          'General\nDescending',
                          'Neighborhood\nAscending',
                          'Neighborhood\nDescending',
                      ],
                      index=['Bnei Brak', 'Holon'])
    draw_heatmap(ax[2], df)
    ax[2].set_title(f"Total Infection for - Asymptomatic Detection")

    df = pd.DataFrame(total_critical_asymptomatic_detection,
                      columns=[
                          'General\nAscending',
                          'General\nDescending',
                          'Neighborhood\nAscending',
                          'Neighborhood\nDescending',
                      ],
                      index=['Bnei Brak', 'Holon'])
    draw_heatmap(ax[3], df)
    ax[3].set_title(f"Total Critical for - Asymptomatic Detection")

    # ------------------------------------------------------------------------------------------------
    total_infections = [0, 0]
    total_infections[0] = total_infections_hh_isolation[0] + total_infections_asymptomatic_detection[0]
    total_infections[1] = total_infections_hh_isolation[1] + total_infections_asymptomatic_detection[1]

    df = pd.DataFrame(total_infections,
                      columns=[
                          'hh_isolation\nGeneral\nAscending',
                          'hh_isolation\nGeneral\nDescending',
                          'hh_isolation\nNeighborhood\nAscending',
                          'hh_isolation\nNeighborhood\nDescending',
                          'asymptomatic isolation\nGeneral\nAscending',
                          'asymptomatic isolation\n\nGeneral\nDescending',
                          'asymptomatic isolation\n\nNeighborhood\nAscending',
                          'asymptomatic isolation\n\nNeighborhood\nDescending',
                      ],
                      index=['Bnei Brak', 'Holon'])
    draw_heatmap(ax[4], df)
    ax[4].set_title(f"Total Infections")

    total_critical = [0, 0]
    total_critical[0] = total_critical_hh_isolation[0] + total_critical_asymptomatic_detection[0]
    total_critical[1] = total_critical_hh_isolation[1] + total_critical_asymptomatic_detection[1]

    df = pd.DataFrame(total_critical,
                      columns=[
                          'hh_isolation\nGeneral\nAscending',
                          'hh_isolation\nGeneral\nDescending',
                          'hh_isolation\nNeighborhood\nAscending',
                          'hh_isolation\nNeighborhood\nDescending',
                          'asymptomatic isolation\nGeneral\nAscending',
                          'asymptomatic isolation\nGeneral\nDescending',
                          'asymptomatic isolation\nNeighborhood\nAscending',
                          'asymptomatic isolation\nNeighborhood\nDescending',
                      ],
                      index=['Bnei Brak', 'Holon'])
    draw_heatmap(ax[5], df)
    ax[5].set_title(f"Total Hospitalization")

    total_infected_combinations = [0]
    total_infected_combinations[0] = total_infection_hh_both_cities_detection + \
                                     total_infections_asymptomatic_both_cities_detection

    df = pd.DataFrame(total_infected_combinations,
                      columns=[
                          'hh_isolation\nGeneral\nAscending',
                          'hh_isolation\nGeneral\nDescending',
                          'hh_isolation\nNeighborhood\nAscending',
                          'hh_isolation\nNeighborhood\nDescending',
                          'hh_isolation\nBnei Brak - ND\nHolon - NA',
                          'hh_isolation\nBnei Brak - GD\nHolon - ND',
                          'asymptomatic isolation\nGeneral\nAscending',
                          'asymptomatic isolation\nGeneral\nDescending',
                          'asymptomatic isolation\nNeighborhood\nAscending',
                          'asymptomatic isolation\nNeighborhood\nDescending',
                          'asymptomatic isolation\nBnei Brak - GD\nHolon - ND'
                      ],
                      index=['Bnei Brak+Holon'])
    draw_heatmap(ax[6], df)
    ax[6].set_title(f"Total Infected - Both Cities")

    total_critical_combinations = [0]
    total_critical_combinations[0] = total_critical_hh_both_cities_detection + \
                                     total_critical_asymptomatic_both_cities_detection

    df = pd.DataFrame(total_critical_combinations,
                      columns=[
                          'hh_isolation\nGeneral\nAscending',
                          'hh_isolation\nGeneral\nDescending',
                          'hh_isolation\nNeighborhood\nAscending',
                          'hh_isolation\nNeighborhood\nDescending',
                          'hh_isolation\nBnei Brak - ND\nHolon - NA',
                          'hh_isolation\nBnei Brak - GD\nHolon - ND',
                          'asymptomatic isolation\nGeneral\nAscending',
                          'asymptomatic isolation\nGeneral\nDescending',
                          'asymptomatic isolation\nNeighborhood\nAscending',
                          'asymptomatic isolation\nNeighborhood\nDescending',
                          'asymptomatic isolation\nBnei Brak - GD\nHolon - ND'
                      ],
                      index=['Bnei Brak+Holon'])
    draw_heatmap(ax[7], df)
    ax[7].set_title(f"Total Hospitalised - Both Cities")

    # ------------------------------------------------------------------------------------------------
    fig.tight_layout(pad=12.0)
    fig.savefig(f"../../outputs/{sys.argv[1]}/heatmap.svg")

    # fig.set_figwidth(16)
    # fig.set_figheight(plots * 30)
