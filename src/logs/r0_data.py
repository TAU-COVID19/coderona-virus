from datetime import timedelta
import numpy as np

from typing import List
from src.world import Person
from src.world.infection_data import InfectionData


def calculate_r0_data(population: List[Person], max_date=None):
    """
    Calculates daily avg r data.
    Returns a dictionary that contains an array of dates, an array of avg r values,
    and an array of smoothed avg values.
    If no valid infections were made, returns None
    population: List[Person]
    """

    # a dictionary where the key is a Person and the
    # value is the [infection date, number-of-people-that-this-person-infected]
    # note: rs is calculated even for dates after "max_date"
    rs = {p: [None, 0] for p in population}
    for p in population:
        infection_data: InfectionData = p.get_infection_data()
        if (infection_data is not None) and (infection_data.date is not None):
            rs[p][0] = infection_data.date
            if infection_data.transmitter is not None:
                rs[infection_data.transmitter][1] += 1

    valid_infections = any(p.get_infection_data().date is not None for p in population
                                if (p.get_infection_data() is not None)
                           )
    if not valid_infections:
        return None

    max_infection_date = max(p.get_infection_data().date for p in population
                                if (p.get_infection_data() is not None) and
                                (p.get_infection_data().date is not None)
                             )
    min_infection_date = min(p.get_infection_data().date for p in population
                                if (p.get_infection_data() is not None) and
                                (p.get_infection_data().date is not None)
                             )
    r0_by_infection_date_pre_division = {
        # for every date [number-of-people-got-infected-today,
        #                 cumulative-number-of-people-infected-since-that-date]
        min_infection_date + timedelta(days=i): [0, 0, 0]
        for i in range((max_infection_date - min_infection_date).days + 1)
    }

    # TODO: r0_by_infection_date_pre_division[date] may get dates out of the range:
    #          min_infection_date..max_infection_date
    # TODO: also, the "infections" may count people who got infected After the max_infection_date
    # TODO: Ask what's the difference between: r0_by_infection_date_pre_division[date][1]
    #       and r0_by_infection_date_pre_division[date][2] ?
    for date, infections in rs.values():
        if date is not None:
            # the date is the date where the person got sick
            r0_by_infection_date_pre_division[date][0] += 1  # how many people who got-infected today
            r0_by_infection_date_pre_division[date][1] += infections  # sum of all of the people who were
                                                                    # infected by a person who got sick today

    for p in population:
        if (p.get_infection_data() is not None) and (p.get_infection_data().date is not None):
            r0_by_infection_date_pre_division[p.get_infection_data().date][2] += p._num_infections

    max_date = max_infection_date if not max_date else max_date
    r0_by_infection_date = [
        (date, (
            total_infected / num_infecting if num_infecting > 0 else np.NaN,
            smoothed_num_infected / num_infecting if num_infecting > 0 else np.NaN
        ))
        # TODO: seems like the first item is counting the "infected" and not the "infecting" right?
        for date, [num_infecting, total_infected, smoothed_num_infected]
        in r0_by_infection_date_pre_division.items()
        if date <= max_date
    ]
    dates = [c[0] for c in r0_by_infection_date]
    smoothed_avg_r0 = [c[1][1] for c in r0_by_infection_date]
    avg_r0 = [c[1][0] for c in r0_by_infection_date]
    return {'dates': dates, 'smoothed_avg_r0': smoothed_avg_r0, 'avg_r0': avg_r0}
