from datetime import timedelta
import numpy as np

def calculate_r0_data(population, max_date=None):
    """
    Calculates daily avg r data.
    Returns a dictionary that contains an array of dates, an array of avg r values,
    and an array of smoothed avg values.
    If no valid infections were made, returns None
    """
    # rs is dictionary for each person how many he has infected every day
    rs = {p: [None, 0] for p in population}
    for p in population:
        infection_data = p.get_infection_data()
        if (infection_data is not None) and (infection_data.date is not None):
            rs[p][0] = infection_data.date
            if infection_data.transmitter is not None:
                rs[infection_data.transmitter][1] += 1
    
    #Validity check that there ware infecious 
    valid_infections = any(p.get_infection_data().date is not None for p in population
                                if (p.get_infection_data() is not None)
                           )
    if not valid_infections:
        return None

    #The last date someone got infected
    max_infection_date = max(p.get_infection_data().date for p in population
                                if (p.get_infection_data() is not None) and
                                (p.get_infection_data().date is not None)
                             )
    #The first date someone got infected
    min_infection_date = min(p.get_infection_data().date for p in population
                                if (p.get_infection_data() is not None) and
                                (p.get_infection_data().date is not None)
                             )
    #Generating dictionary date:num of infectors, num of infected, how much every person contributed to the infection every day
    r0_by_infection_date_pre_division = {
        min_infection_date + timedelta(days=i): [0, 0, 0]
        for i in range((max_infection_date - min_infection_date).days + 1)
    }
    for date, infections in rs.values():
        if date is not None:
            r0_by_infection_date_pre_division[date][0] += 1
            r0_by_infection_date_pre_division[date][1] += infections

    for p in population:
        if (p.get_infection_data() is not None) and (p.get_infection_data().date is not None):
            r0_by_infection_date_pre_division[p.get_infection_data().date][2] += p._num_infections
    
    #Minimizing the range of simulation results to the necessary 
    max_date = max_infection_date if not max_date else max_date
    
    #Return values of dates: R0 of this date ,smoothed RO if this date
    r0_by_infection_date = [
        (date, (
            total_infected / num_infecting if num_infecting > 0 else np.NaN,
            smoothed_num_infected / num_infecting if num_infecting > 0 else np.NaN
        ))
        for date, [num_infecting, total_infected, smoothed_num_infected]
        in r0_by_infection_date_pre_division.items()
        if date <= max_date
    ]
    dates = [c[0] for c in r0_by_infection_date]
    smoothed_avg_r0 = [c[1][1] for c in r0_by_infection_date]
    avg_r0 = [c[1][0] for c in r0_by_infection_date]
    return {'dates': dates, 'smoothed_avg_r0': smoothed_avg_r0, 'avg_r0': avg_r0}
