from tabulate import tabulate
import pandas as pd
import scipy.stats


def plot_mixed_strategy_confidence_interval(c) -> None:
    """
    calculate the effect of applying different strategies for different cities
    :param c: a list of tuple [(strategy, DataFrame)]
    :return: None
    """
    bootstrap_results = pd.DataFrame(columns=['Strategy 1', 'Strategy 2', 'Confidence Low', 'Confidence High'])
    d = c.head(200)

    # pick specific combinations to compare
    combinations = [
        [
            {"city": "Holon", "vaccination_strategy": "NEIGHBORHOOD", "order": "DESCENDING", "intervention": "hh_isolation"},
            {"city": "Benei Brak", "vaccination_strategy": "GENERAL", "order": "DESCENDING", "intervention": "hh_isolation"},

            {"city": "Holon", "vaccination_strategy": "GENERAL", "order": "DESCENDING", "intervention": "hh_isolation"},
            {"city": "Benei Brak", "vaccination_strategy": "GENERAL", "order": "DESCENDING", "intervention": "hh_isolation"},
        ],

        [
            {"city": "Holon", "vaccination_strategy": "NEIGHBORHOOD", "order": "ASCENDING", "intervention": "hh_isolation"},
            {"city": "Benei Brak", "vaccination_strategy": "NEIGHBORHOOD", "order": "DESCENDING", "intervention": "hh_isolation"},

            {"city": "Holon", "vaccination_strategy": "NEIGHBORHOOD", "order": "ASCENDING", "intervention": "hh_isolation"},
            {"city": "Benei Brak", "vaccination_strategy": "NEIGHBORHOOD", "order": "ASCENDING", "intervention": "hh_isolation"},
        ],

        [
            {"city": "Holon", "vaccination_strategy": "NEIGHBORHOOD", "order": "ASCENDING",
             "intervention": "asymptomatic_detection"},
            {"city": "Benei Brak", "vaccination_strategy": "NEIGHBORHOOD", "order": "DESCENDING",
             "intervention": "asymptomatic_detection"},

            {"city": "Holon", "vaccination_strategy": "NEIGHBORHOOD", "order": "DESCENDING",
             "intervention": "asymptomatic_detection"},
            {"city": "Benei Brak", "vaccination_strategy": "NEIGHBORHOOD", "order": "DESCENDING",
             "intervention": "asymptomatic_detection"},
        ],

        [
            {"city": "Holon", "vaccination_strategy": "NEIGHBORHOOD", "order": "ASCENDING",
             "intervention": "asymptomatic_detection"},
            {"city": "Benei Brak", "vaccination_strategy": "NEIGHBORHOOD", "order": "DESCENDING",
             "intervention": "asymptomatic_detection"},

            {"city": "Holon", "vaccination_strategy": "GENERAL", "order": "DESCENDING",
             "intervention": "asymptomatic_detection"},
            {"city": "Benei Brak", "vaccination_strategy": "GENERAL", "order": "DESCENDING",
             "intervention": "asymptomatic_detection"},
        ],

    ]

    for combination in combinations:
        pair_1_city_1 = d[(d.city == combination[0]["city"]) &
                          (d.vaccination_strategy == combination[0]["vaccination_strategy"]) &
                          (d.order == combination[0]["order"]) &
                          (d.intervention == combination[0]["intervention"])]
        pair_1_city_2 = d[(d.city == combination[1]["city"]) &
                          (d.vaccination_strategy == combination[1]["vaccination_strategy"]) &
                          (d.order == combination[1]["order"]) &
                          (d.intervention == combination[1]["intervention"])]
        pair_2_city_1 = d[(d.city == combination[2]["city"]) &
                          (d.vaccination_strategy == combination[2]["vaccination_strategy"]) &
                          (d.order == combination[2]["order"]) &
                          (d.intervention == combination[2]["intervention"])]
        pair_2_city_2 = d[(d.city == combination[3]["city"]) &
                          (d.vaccination_strategy == combination[3]["vaccination_strategy"]) &
                          (d.order == combination[3]["order"]) &
                          (d.intervention == combination[3]["intervention"])]

        # calculate for hospitalisation
        pair_1 = np.array(pair_1_city_1.total_hospitalized_samples.to_list()) + \
                 np.array(pair_1_city_2.total_hospitalized_samples.to_list())
        pair_2 = np.array(pair_2_city_1.total_hospitalized_samples.to_list()) + \
                 np.array(pair_2_city_2.total_hospitalized_samples.to_list())
        res = scipy.stats.bootstrap(data=(pair_1 - pair_2), statistic=np.mean)
        bootstrap_results = bootstrap_results.append({
            'Strategy 1': f'HOSPITALISATION: {combination[0]["city"]}: {combination[0]["intervention"]} - {combination[0]["vaccination_strategy"]} - {combination[0]["order"]}' + "\n" +
                          f'{combination[1]["city"]}: {combination[1]["intervention"]} - {combination[1]["vaccination_strategy"]} - {combination[1]["order"]}',
            'Strategy 2': f'HOSPITALISATION: {combination[2]["city"]}: {combination[2]["intervention"]} - {combination[2]["vaccination_strategy"]} - {combination[2]["order"]}' + "\n" +
                          f'{combination[3]["city"]}: {combination[3]["intervention"]} - {combination[3]["vaccination_strategy"]} - {combination[3]["order"]}',
            'Confidence Low': res.confidence_interval.low,
            'Confidence High': res.confidence_interval.high,
        }, ignore_index=True)

        # do the same for Infections
        pair_1 = np.array(pair_1_city_1.total_infected_samples.to_list()) + \
                 np.array(pair_1_city_2.total_infected_samples.to_list())
        pair_2 = np.array(pair_2_city_1.total_infected_samples.to_list()) + \
                 np.array(pair_2_city_2.total_infected_samples.to_list())
        res = scipy.stats.bootstrap(data=(pair_1 - pair_2), statistic=np.mean)
        bootstrap_results = bootstrap_results.append({
            'Strategy 1': f'INFECTIONS: {combination[0]["city"]}: {combination[0]["intervention"]} - {combination[0]["vaccination_strategy"]} - {combination[0]["order"]}' + "\n" +
                          f'{combination[1]["city"]}: {combination[1]["intervention"]} - {combination[1]["vaccination_strategy"]} - {combination[1]["order"]}',
            'Strategy 2': f'INFECTIONS: {combination[2]["city"]}: {combination[2]["intervention"]} - {combination[2]["vaccination_strategy"]} - {combination[2]["order"]}' + "\n" +
                          f'{combination[3]["city"]}: {combination[3]["intervention"]} - {combination[3]["vaccination_strategy"]} - {combination[3]["order"]}',
            'Confidence Low': res.confidence_interval.low,
            'Confidence High': res.confidence_interval.high,
        }, ignore_index=True)

    print(f"\n{combinations}")
    print(tabulate(bootstrap_results, headers='keys', tablefmt='fancy_grid'))
    bootstrap_results.to_csv(f'{root_path}/outputs/{sys.argv[1]}/bootstrap_combinations.csv')
    bootstrap_results.to_html(f'{root_path}/outputs/{sys.argv[1]}/bootstrap_combinations.html')
