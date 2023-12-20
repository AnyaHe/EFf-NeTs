import pandas as pd

from indicators import get_fairness, get_expansion_der,\
    get_efficient_electricity_usage, get_efficient_grid, \
    add_names_criteria


def get_performance_indicators_scenario_with_names(
        dt, idx_scenario, nr_alternatives, alternative_names=None):
    """
    Method for calculation of indicators for specific scenario.

    :param dt: pd.DataFrame
        input data
    :param idx_scenario: int
        scenario to be analysed
    :param nr_alternatives: int
        total number of alternatives
    :param alternative_names: list of str or None (default)
        names of investigated alternatives, defaults to ['Volumetric Tariff',
        'Monthly Power Peak', 'Yearly Power Peak', 'Capacity Tariff']
    :return:
    """
    result_matrix = \
        get_performance_indicators_scenario(dt, idx_scenario, nr_alternatives)
    if alternative_names is None:
        alternative_names = ['Volumetric Tariff', 'Monthly Power Peak',
                             'Yearly Power Peak', 'Capacity Tariff']
    result_matrix.columns = alternative_names
    # result_matrix['Criteria'] = names_criteria()
    result_matrix['Scenario'] = idx_scenario

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


def get_results(dt, nr_scenarios, nr_alternatives, weights, scenario_names=None):
    """
    Aggregating results for all scenarios

    :param dt: pd.DataFrame
        input data
    :param nr_scenarios: int
        total number of simulated scenarios
    :param nr_alternatives: int
        total number of alternatives
    :param weights: pd.DataFrame
        dataframe with weighting of indicators
    :param scenario_names: list of str or None (default)
        names of investigated scenarios, defaults to ['Scenario 1', 'Scenario 2',
        'Scenario 3', 'Scenario 4']
    :return:
    """

    results_final = pd.concat([
        get_rating_scenario(
            dt=dt, idx_scenario=i+1, nr_alternatives=nr_alternatives, weights=weights)
        for i in range(nr_scenarios)], axis=1)
    if scenario_names is None:
        scenario_names = ['Scenario 1', 'Scenario 2', 'Scenario 3', 'Scenario 4']
    results_final.columns = scenario_names

    return results_final
