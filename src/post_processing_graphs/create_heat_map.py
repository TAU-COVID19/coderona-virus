import sys

from matplotlib import pyplot
import seaborn as sns
import pandas as pd


def draw_heatmap(ax, df: pd.DataFrame):
    sns.set_theme()
    sns.heatmap(data=df, ax=ax)
    # ax.legend()


if __name__ == "__main__":
    plots = 4
    fig, ax = pyplot.subplots(plots, 1)
    fig.set_figwidth(16)
    fig.set_figheight(plots * 10)

    # ----------- FILL HERE THE REAL DATA ------------

    # ----------- START ------------
    total_infections_hh_isolation = [
        (10, 20, 30, 40),  # Bnei Brak
        (30, 60, 10, 80)]  # Holon

    total_critical_hh_isolation = [
        (10, 20, 30, 40),  # Bnei Brak
        (30, 60, 10, 80)]  # Holon

    # List of tuples
    total_infections_asymptomatic_detection = [
        (10, 20, 30, 40),  # Bnei Brak
        (30, 60, 10, 80)]  # Holon

    total_critical_asymptomatic_detection = [
        (10, 20, 30, 40),  # Bnei Brak
        (30, 60, 10, 80)]  # Holon
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

    fig.tight_layout(pad=12.0)
    fig.savefig(f"../../outputs/{sys.argv[1]}/heatmap.svg")

    # fig.set_figwidth(16)
    # fig.set_figheight(plots * 30)
