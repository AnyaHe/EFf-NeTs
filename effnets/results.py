import pandas as pd

from indicators import get_fairness, get_expansion_der,\
    get_efficient_electricity_usage, get_efficient_grid
from weights import add_names_criteria


def get_performance_indicators_scenario_with_names(dt, sf, af):
    result_matrix = get_performance_indicators_scenario(dt, sf, af)
    result_matrix.columns = \
        ['Volumetric Tariff', 'Monthly Power Peak', 'Yearly Power Peak',
         'Capacity Tariff']
    result_matrix['Criteria'] = ['Efficient Grid',
                                 'Fairness and Customer Acceptance',
                                 'Expansion of DER',
                                 'Efficient Electricity Usage'] # Todo: connect with add_names_criteria
    result_matrix['Scenario'] = sf

    return result_matrix


def get_performance_indicators_scenario(dt, idx_scenario, nr_alternatives):
    """
    Normalised results for indicators

    :param dt: pd.DataFrame
        input data
    :param idx_scenario: int
        scenario to be analysed
    :param nr_alternatives: int
        total number of alternatives
    :return:
    """
    efficient_grid = get_efficient_grid(dt, idx_scenario, nr_alternatives)
    fairness_and_customer_acceptance = get_fairness(dt, idx_scenario, nr_alternatives)
    expansion_der = get_expansion_der(dt, idx_scenario, nr_alternatives)
    efficient_electricity_usage = \
        get_efficient_electricity_usage(dt, idx_scenario, nr_alternatives)
    result_matrix = pd.concat([efficient_grid,
                               fairness_and_customer_acceptance,
                               expansion_der,
                               efficient_electricity_usage], ignore_index=True)
    return add_names_criteria(result_matrix.T).T


def get_rating_scenario(dt, idx_scenario, nr_alternatives, weights):
    """
    Combining indicator results with criteria weights to generate ranking

    :param dt: pd.DataFrame
        input data
    :param idx_scenario: int
        scenario to be analysed
    :param nr_alternatives: int
        total number of alternatives
    :param weights: pd.DataFrame
        dataframe with weighting of indicators
    :return:
    """
    performance_indicators = \
        get_performance_indicators_scenario(dt, idx_scenario, nr_alternatives)

    for alternative in range(1, len(performance_indicators.columns) + 1):
        performance_indicators[alternative] = \
            performance_indicators[alternative] * weights.transpose().iloc[:, 0]

    overall_rating = performance_indicators.sum()

    return overall_rating


def get_results(dt, nr_alternatives, weights):
    """
    Aggregating results for all scenarios

    :param dt: pd.DataFrame
        input data
    :param nr_alternatives: int
        total number of alternatives
    :param weights: pd.DataFrame
        dataframe with weighting of indicators
    :return:
    """
    results_scenario_1 = get_rating_scenario(dt, 1, nr_alternatives, weights)
    results_scenario_2 = get_rating_scenario(dt, 2, nr_alternatives, weights)
    results_scenario_3 = get_rating_scenario(dt, 3, nr_alternatives, weights)
    results_scenario_4 = get_rating_scenario(dt, 4, nr_alternatives, weights)

    results_final = pd.concat([results_scenario_1, results_scenario_2,
                               results_scenario_3, results_scenario_4], axis=1)
    results_final.columns = ['Scenario 1', 'Scenario 2', 'Scenario 3', 'Scenario 4']

    return results_final
