from simulation.mock_simulation import InitialStateSimulation


class InitialInfectionParams(object):
    """
    Base abstract class that defines the behavior of infecting an initial set of people at the start of the simulation.
    Each subclass has to implement a way to infect an initial set in a simulation object.
    """
    def __init__(self):
        pass

    def infect_simulation(self, sim, outdir):
        raise NotImplementedError()


class NaiveInitialInfectionParams(InitialInfectionParams):
    """
    Infect num_to_infect random people in city_name_to_infect
    or in the entire country if city_name_to_infect is not given
    """
    def __init__(self, num_to_infect, city_name_to_infect=None):
        super(NaiveInitialInfectionParams, self).__init__()
        self.num_to_infect = num_to_infect
        self.city_name_to_infect = city_name_to_infect

    def infect_simulation(self, sim, outdir):
        sim.infect_random_set(self.num_to_infect, str(self), self.city_name_to_infect)

    def __str__(self):
        if self.city_name_to_infect is None:
            return "{}(num_to_infect={})".format(self.__class__.__name__, self.num_to_infect)
        return "{}(num_to_infect={}, city_name_to_infect={})".format(
            self.__class__.__name__, self.num_to_infect, self.city_name_to_infect
        )


class SmartInitialInfectionParams(InitialInfectionParams):
    """
    This subclass defines a "smart" way to infect - runs a "mock" simulation until the requested amount of 'symptomatic or post-symptomatic' are reached.

    initial_symptomatic_num_in_each_city is a dict from a city to the number of 'symptomatic or post-symptomatic' people that city should have.
    The simulation will infect initial_random_set_for_mock and then wait until the appropriate numbers infected in each city.
    It will 'copy' the disease states in each city corresponding to that city's
    point in time (when the 'symptomatic or post-symptomatic' number was right).
    """
    def __init__(self, initial_symptomatic_num_in_each_city, initial_random_set_for_mock):
        super(SmartInitialInfectionParams, self).__init__()
        self.initial_symptomatic_num_in_each_city = initial_symptomatic_num_in_each_city
        self.initial_random_set_for_mock = initial_random_set_for_mock

    def infect_simulation(self, sim, outdir):
        mock_sim = InitialStateSimulation(
            sim._world,
            sim._initial_date,
            None,
            verbosity=False,
            outdir=outdir
        )
        mock_sim.infect_random_set(self.initial_random_set_for_mock, "N/A", None)
        initial_infections = mock_sim.get_initial_infections(
            {city: self.initial_symptomatic_num_in_each_city for city in sim._world.get_all_city_names()}
        )
        for e in sim._world.all_environments:
            e.clear()

        sim._world.sign_all_people_up_to_environments()
        sim.infect_chosen_set(initial_infections, str(self))

    def __str__(self):
        return "{}(initial_symptomatic_num_in_each_city={}, initial_random_set_for_mock={})".format(
            self.__class__.__name__, self.initial_symptomatic_num_in_each_city, self.initial_random_set_for_mock
        )
