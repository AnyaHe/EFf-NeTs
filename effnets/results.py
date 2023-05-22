import pandas as pd

from indicators import usage_related, capacity_related, fairness, expansion_der,\
    electricity_related
from weights import addnames


def r_matrix(dt, sf, af):
    r = result_matrix(dt, sf, af)
    r.columns = ['1 Volumetric Tariff', '2 Monthly Power Peak', '3 Yearly Power Peak',
                 '4 Capacity Tariff']
    r['Criteria'] = ['1 Reflection of Usage-Related Costs',
                     '2 Reflection of Capacity-Related Costs',
                     '3 Fairness and Customer Acceptance',
                     '4 Expansion of DER',
                     '5 Efficient Electricity Usage']
    r['Scenario'] = [sf, sf, sf, sf, sf]

    return r


def result_matrix(dt, sf, af):
    """
    Normalised results for indicators

    :param dt: pd.DataFrame
        input data
    :param sf: int
        scenario to be analysed
    :param af: int
        total number of alternatives
    :return:
    """
    UR = usage_related(dt, sf, af)
    CR = capacity_related(dt, sf, af)
    N = fairness(dt, sf, af)
    FR = N.div(N.sum(axis=1), axis=0)
    RR = expansion_der(dt, sf, af)
    EF = electricity_related(dt, sf, af)
    rf = pd.concat([UR, CR, FR, RR, EF], ignore_index=True)
    return addnames(rf.T).T


def end_result(dt, sf, af, weights):
    """
    Combining indicator results with criteria's weights to generate ranking

    :param dt: pd.DataFrame
        input data
    :param sf: int
        scenario to be analysed
    :param af: int
        total number of alternatives
    :param weights: pd.DataFrame
        dataframe with weighting of indicators
    :return:
    """
    N = result_matrix(dt, sf, af)

    for j in range(1, len(N.columns) + 1):
        N[j] = N[j] * weights.transpose().iloc[:, 0]

    R = N.sum()

    return R


def results(dt, af, weights):
    """
    Aggregating results for all scenarios

    :param dt: pd.DataFrame
        input data
    :param af: int
        total number of alternatives
    :param weights: pd.DataFrame
        dataframe with weighting of indicators
    :return:
    """
    S1 = end_result(dt, 1, af, weights)
    S2 = end_result(dt, 2, af, weights)
    S3 = end_result(dt, 3, af, weights)
    S4 = end_result(dt, 4, af, weights)

    S = pd.concat([S1, S2, S3, S4], axis=1)
    S.columns = ['Scenario 1', 'Scenario 2', 'Scenario 3', 'Scenario 4']

    return S
