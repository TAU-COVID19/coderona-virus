from src.world.environments.homogeneous_environment import HomogeneousEnvironment


class NeighborhoodCommunity(HomogeneousEnvironment):
    __slots__ = ('_city', '_city_env')
    name = "neighborhood_community"

    def __init__(self, city, contact_prob_between_each_two_people):
        super(NeighborhoodCommunity, self).__init__(contact_prob_between_each_two_people)
        self._city = city
        self._city_env = None

    def set_city_env(self, city_env):
        self._city_env = city_env
