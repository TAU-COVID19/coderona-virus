from world.environments.homogeneous_environment import HomogeneousEnvironment


class Household(HomogeneousEnvironment):
    __slots__ = ('_city', '_city_env')
    name = "household"

    def __init__(self, city, contact_prob_between_each_two_people):
        super(Household, self).__init__(contact_prob_between_each_two_people)
        self._city = city
        self._city_env = None

    def set_city_env(self, city_env):
        self._city_env = city_env
