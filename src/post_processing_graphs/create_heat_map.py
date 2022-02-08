import sys

from matplotlib import pyplot
import seaborn as sns
import pandas as pd


def draw_heatmap(ax, df: pd.DataFrame):
    sns.set_theme()
    sns.heatmap(data=df, ax=ax, cmap="Spectral_r", annot=True, fmt=",.0f")
    # ax.legend()


if __name__ == "__main__":
    plots = 6
    fig, ax = pyplot.subplots(plots, 1)
    fig.set_figwidth(16)
    fig.set_figheight(plots * 10)

    # ----------- FILL HERE THE REAL DATA ------------

    # ----------- START ------------
    total_infections_hh_isolation = [
        (20124.048, 21815.344, 21284.386, 20583.918),  # Bnei Brak
        (3086.912, 6444.378, 3089.04, 4050.756)]  # Holon

    total_critical_hh_isolation = [
        (69.8, 3.43, 17.272, 10.15),  # Bnei Brak
        (27.92, 6.5, 16.53, 12.04)]  # Holon

    # List of tuples
    total_infections_asymptomatic_detection = [
        (1611.998, 1966.822, 1537.38, 1522.086),  # Bnei Brak
        (1050.884, 2070.666, 1115.59, 1346.112)]  # Holon

    total_critical_asymptomatic_detection = [
        (7.248, 0.888, 2.43, 1.944),  # Bnei Brak
        (12.046, 4.802, 8.886, 7.37)]  # Holon
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
                          'asymptomatic isolation\n\nGeneral\nDescending',
                          'asymptomatic isolation\n\nNeighborhood\nAscending',
                          'asymptomatic isolation\n\nNeighborhood\nDescending',
                      ],
                      index=['Bnei Brak', 'Holon'])
    draw_heatmap(ax[5], df)
    ax[5].set_title(f"Total Critical")

    # ------------------------------------------------------------------------------------------------
    fig.tight_layout(pad=12.0)
    fig.savefig(f"../../outputs/{sys.argv[1]}/heatmap.svg")

    # fig.set_figwidth(16)
    # fig.set_figheight(plots * 30)
