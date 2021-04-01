import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) # Adding the src folder to PYTHONPATH

from src.scenarios import paper_8
from src.simulation.initial_infection_params import NaiveInitialInfectionParams
from src.run_utils import RepeatJob, SimpleJob, run


def test_paper_8_bug():
    jobs = []
    for city in ["Holon", "Bene Beraq"]:
        for initial_num_infected in [25, 100, 250, 500]:
            name = "paper 8 bug_City:{}_Initial infected:{}".format(city, initial_num_infected)
            jobs.append(RepeatJob(SimpleJob(
                            days=180,
                            scenario_name = name,
                            city_name=city,
                            infection_params=NaiveInitialInfectionParams(initial_num_infected),
                            interventions=paper_8()
    ), 20))
    run(jobs, with_population_caching=False, verbosity=False)

if __name__ == "__main__":
    test_paper_8_bug()