from src.scenarios import paper_8
from src.simulation.initial_infection_params import NaiveInitialInfectionParams
from src.run_utils import RepeatJob, SimpleJob, run


def test_paper_8_bug():
    jobs = []
    for percent_immune in [0.0]:
        for city in ["Holon", "Bene Beraq"]:
            for initial_num_infected in [25, 100, 250, 500]:
                name = "{}:{} initial infected:{} percent immune, paper_8_bug".format(city, initial_num_infected, percent_immune)
                jobs.append(RepeatJob(SimpleJob(
                                days=180,
                                scenario_name = name,
                                city_name=city,
                                infection_params=NaiveInitialInfectionParams(initial_num_infected, per_to_Immune=percent_immune),
                                interventions=paper_8()
    ), 20))
    run(jobs, with_population_caching=False, verbosity=False)

