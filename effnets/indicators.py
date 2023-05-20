import pandas as pd
import numpy as np
from weights import addnames


# Implementation of the indicators with functions


def peak_ratio(dt, sf, af):
    """
    Calculating Peak Impact Cost Ratio for an Alternative and Scenario

    :param dt: pd.DataFrame
        input data
    :param sf: int
        scenario to be analysed
    :param af: int
        total number of alternatives
    :return:
    """
    rf = pd.DataFrame()
    for i in range(1, af + 1):
        fl = dt[(dt['Scenario'] == sf) & (dt['Alternative'] == i)]
        rf.loc[0, i] = fl['Weighted Peak Ratio'].sum()

    A = (np.power(10, rf)).rdiv(1)
    N = A.div(A.sum(axis=1), axis=0)
    return N


def peak_total(dt, sf, af):
    """
    Calculating Simultaneous Peak for an Alternative and Scenario

    :param dt: pd.DataFrame
        input data
    :param sf: int
        scenario to be analysed
    :param af: int
        total number of alternatives
    :return:
    """
    rf = pd.DataFrame()
    for i in range(1, af + 1):
        fl = dt[(dt['Scenario'] == sf) & (dt['Alternative'] == i)]
        rf.loc[0, i] = fl['Simultaneous Peak'].sum()

    A = rf.rdiv(1)
    N = A.div(A.sum(axis=1), axis=0)
    return N


def usage_related(dt, sf, af):
    """
    Calculating Usage (Peak) Related Distribution Factor for All Alternatives in given
    Scenario

    :param dt: pd.DataFrame
        input data
    :param sf: int
        scenario to be analysed
    :param af: int
        total number of alternatives
    :return:
    """
    A = peak_ratio(dt, sf, af) + peak_total(dt, sf, af)
    N = A.div(A.sum(axis=1), axis=0)
    return N


def capacity_ratio(dt, sf, af):
    """
    Calculating Contracted Capacity-Cost Ratio for an Alternative and Scenario

    :param dt: pd.DataFrame
        input data
    :param sf: int
        scenario to be analysed
    :param af: int
        total number of alternatives
    :return:
    """
    rf = pd.DataFrame()
    for i in range(1, af + 1):
        fl = dt[(dt['Scenario'] == sf) & (dt['Alternative'] == i)]
        rf.loc[0, i] = fl['Weighted Capacity Ratio'].sum()

    A = (np.power(10, rf)).rdiv(1)
    N = A.div(A.sum(axis=1), axis=0)
    return N


def capacity_total(dt, sf, af):
    """
    Calculating the total Contracted Capacity for an Alternative and Scenario

    :param dt: pd.DataFrame
        input data
    :param sf: int
        scenario to be analysed
    :param af: int
        total number of alternatives
    :return:
    """
    rf = pd.DataFrame()
    for i in range(1, af + 1):
        fl = dt[(dt['Scenario'] == sf) & (dt['Alternative'] == i)]
        rf.loc[0, i] = fl['Contracted Capacity'].sum()

    A = rf.rdiv(1)
    N = A.div(A.sum(axis=1), axis=0)
    return N


def capacity_related(dt, sf, af):
    """
    Calculating Capacity Related Distribution Factor for All Alternatives

    :param dt: pd.DataFrame
        input data
    :param sf: int
        scenario to be analysed
    :param af: int
        total number of alternatives
    :return:
    """
    A = capacity_ratio(dt, sf, af) + capacity_total(dt, sf, af)
    N = A.div(A.sum(axis=1), axis=0)
    return N


def fairness(dt, sf, af):
    """
    Relative Cost Share of Inflexible Customers (Reference Value)

    :param dt: pd.DataFrame
        input data
    :param sf: int
        scenario to be analysed
    :param af: int
        total number of alternatives
    :return:
    """
    f1 = dt[(dt['Scenario'] == 1) & (dt['Alternative'] == 1) & (dt['Customer Group'] == 1)]
    f_bas = f1['Relative Cost Share'].values[0]
    # f_bas = f1.loc[0, 'Relative Cost Share']

    # Calculating Fairness and Customer Acceptance Ratio
    f2 = dt[(dt['Customer Group'] == 1)].copy()
    f2['Fairness'] = np.log10(f_bas / f2['Relative Cost Share'])
    # f2.assign(Fairness=lambda x: f2['Relative Cost Share'] / f_bas)

    rf = pd.DataFrame()

    for i in range(1, af + 1):
        fl = f2[(f2['Scenario'] == sf) & (f2['Alternative'] == i)]
        rf.loc[0, i] = fl['Fairness'].values[0]

    A = np.power(10, rf)
    return A


def pvcost_ratio(dt, sf, af):
    """
    Do PV Owners pay more or less under a given tariff than under a volumetric tariff
    (relative to their purchased electricity share)

    :param dt: pd.DataFrame
        input data
    :param sf: int
        scenario to be analysed
    :param af: int
        total number of alternatives
    :return:
    """
    # Relative Cost Share of Customer Group 2 (Reference Value)
    f1 = dt[(dt['Scenario'] == sf) & (dt['Alternative'] == 1) & (dt['Customer Group'] == 2)]
    f_ref = f1['Relative Cost Share'].values[0]
    # f_bas = f1.loc[0, 'Relative Cost Share']

    # Calculating the PV Cost Ratio under given alternatives
    f2 = dt[(dt['Customer Group'] == 2)].copy()
    f2['PV Cost Ratio'] = f_ref / f2['Relative Cost Share']

    R = pd.DataFrame()

    for i in range(1, af + 1):
        fl = f2[(f2['Scenario'] == sf) & (f2['Alternative'] == i)]
        R.loc[0, i] = fl['PV Cost Ratio'].values[0]

    return R


def pv_rentability(dt, sf, af):
    """
    How much can inflexible consumers save by purchasing a PV System?

    :param dt: pd.DataFrame
        input data
    :param sf: int
        scenario to be analysed
    :param af: int
        total number of alternatives
    :return:
    """
    A = [[1.162, 1.0133, 1.0053, 1]] # Determined based on example consumer profiles
    B = pd.DataFrame(A, columns=[1, 2, 3, 4])

    return B


def expansion_der(dt, sf, af):
    """
    Calculating indicator for criterion of expanding DER for All Alternatives

    :param dt: pd.DataFrame
        input data
    :param sf: int
        scenario to be analysed
    :param af: int
        total number of alternatives
    :return:
    """
    M = pvcost_ratio(dt, sf, af)
    N = M.div(M.sum(axis=1), axis=0)
    O = pv_rentability(dt, sf, af)
    P = O.div(O.sum(axis=1), axis=0)
    A = N + P
    B = A.div(A.sum(axis=1), axis=0)
    return B


def electricity_ratio(dt, sf, af):
    """
    Calculating Efficient Electricity Usage Ratio for an Alternative and Scenario

    :param dt: pd.DataFrame
        input data
    :param sf: int
        scenario to be analysed
    :param af: int
        total number of alternatives
    :return:
    """
    rf = pd.DataFrame()

    for i in range(1, af + 1):
        fl = dt[(dt['Scenario'] == sf) & (dt['Alternative'] == i)]
        rf.loc[0, i] = fl['Weighted Efficiency Ratio'].sum()

    A = (np.power(10, rf)).rdiv(1)
    N = A.div(A.sum(axis=1), axis=0)
    return N


def electricity_total(dt, sf, af):
    """
    Calculating the total Electricity Purchased for an Alternative and Scenario

    :param dt: pd.DataFrame
        input data
    :param sf: int
        scenario to be analysed
    :param af: int
        total number of alternatives
    :return:
    """
    rf = pd.DataFrame()
    for i in range(1, af + 1):
        fl = dt[(dt['Scenario'] == sf) & (dt['Alternative'] == i)]
        rf.loc[0, i] = fl['Electricity Purchased'].sum()

    A = rf.rdiv(1)
    N = A.div(A.sum(axis=1), axis=0)
    return N


def electricity_related(dt, sf, af):
    """
    Calculating Efficient Electricity Usage for all Alternatives

    :param dt: pd.DataFrame
        input data
    :param sf: int
        scenario to be analysed
    :param af: int
        total number of alternatives
    :return:
    """
    A = electricity_ratio(dt, sf, af) + electricity_total(dt, sf, af)
    N = A.div(A.sum(axis=1), axis=0)
    return N
