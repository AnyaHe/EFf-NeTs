import pandas as pd
import openpyxl as openpyxl
import numpy as np
import matplotlib.pyplot as plt
from weights import *

# Number of scenarios
s = 4
# Number of alternatives
a = 4
# Number of criteria
c = 5

# Import input data from simulated network
data = pd.read_excel(r'data/inputdata.xlsx',
                     sheet_name='Input')
df = pd.DataFrame(data, columns=['Scenario', 'Alternative', 'Customer Group', 'Group Share', 'Cost Share', 'Peak Share',
                                 'Capacity Share', 'Energy Share', 'Electricity Purchased', 'Simultaneous Peak',
                                 'Contracted Capacity', 'Local Peak'])

# Auxiliary values
df['Relative Cost Share'] = df['Cost Share'] / df['Energy Share']
df['Peak Ratio'] = df['Peak Share']/df['Cost Share']
df['Capacity Ratio'] = df['Capacity Share']/df['Cost Share']
df['Energy Ratio'] = df['Energy Share']/df['Cost Share']

df['Weighted Peak Ratio'] = (np.log10(df['Peak Ratio']) * df['Group Share']).abs()
df['Weighted Capacity Ratio'] = (np.log10(df['Capacity Ratio']) * df['Group Share']).abs()
df['Weighted Efficiency Ratio'] = (np.log10(df['Energy Ratio']) * df['Group Share']).abs()

# Implementation of the indicators with functions.
# The functions demand as input: dt: dataframe with input data, sf: scenario to be analysed, af: total number of alternatives

def peak_ratio(dt, sf, af):
    # Calculating Peak Impact Cost Ratio for an Alternative and Scenario
    rf = pd.DataFrame()
    for i in range(1, af + 1):
        fl = dt[(dt['Scenario'] == sf) & (dt['Alternative'] == i)]
        rf.loc[0, i] = fl['Weighted Peak Ratio'].sum()

    A = (np.power(10, rf)).rdiv(1)
    N = A.div(A.sum(axis=1), axis=0)
    return N

def peak_total(dt, sf, af):
    # Calculating Simultaneous Peak for an Alternative and Scenario
    rf = pd.DataFrame()
    for i in range(1, af + 1):
        fl = dt[(dt['Scenario'] == sf) & (dt['Alternative'] == i)]
        rf.loc[0, i] = fl['Simultaneous Peak'].sum()

    A = rf.rdiv(1)
    N = A.div(A.sum(axis=1), axis=0)
    return N

def usage_related(dt, sf, af):
    # Calculating Usage (Peak) Related Distribution Factor for All Alternatives in given Scenario
    A = peak_ratio(dt, sf, af) + peak_total(dt, sf, af)
    N = A.div(A.sum(axis=1), axis=0)
    return N

def capacity_ratio(dt, sf, af):
    # Calculating Contracted Capacity-Cost Ratio for an Alternative and Scenario
    rf = pd.DataFrame()
    for i in range(1, af + 1):
        fl = dt[(dt['Scenario'] == sf) & (dt['Alternative'] == i)]
        rf.loc[0, i] = fl['Weighted Capacity Ratio'].sum()

    A = (np.power(10, rf)).rdiv(1)
    N = A.div(A.sum(axis=1), axis=0)
    return N

def capacity_total(dt, sf, af):
    # Calculating the total Contracted Capacity for an Alternative and Scenario
    rf = pd.DataFrame()
    for i in range(1, af + 1):
        fl = dt[(dt['Scenario'] == sf) & (dt['Alternative'] == i)]
        rf.loc[0, i] = fl['Contracted Capacity'].sum()

    A = rf.rdiv(1)
    N = A.div(A.sum(axis=1), axis=0)
    return N

def capacity_related(dt, sf, af):
    # Calculating Capacity Related Distribution Factor for All Alternatives
    A = capacity_ratio(dt, sf, af) + capacity_total(dt, sf, af)
    N = A.div(A.sum(axis=1), axis=0)
    return N

def fairness(dt, sf, af):
    # Relative Cost Share of Inflexible Customers (Reference Value)
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
    # Do PV Owners pay more or less under a given tariff than under a volumetric tariff (relative to their purchased electricity share)
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
    # How much can inflexible consumers save by purchasing a PV System?
    A = [[1.162, 1.0133, 1.0053, 1]] # Determined based on example consumer profiles
    B = pd.DataFrame(A, columns =[1, 2, 3, 4])

    return B


def expansion_der(dt, sf, af):
    # Calculating indicator for criterion of expanding DER for All Alternatives
    M = pvcost_ratio(dt, sf, af)
    N = M.div(M.sum(axis=1), axis = 0)
    O = pv_rentability(df, sf, af)
    P = O.div(O.sum(axis=1), axis =0)
    A = N + P
    B = A.div(A.sum(axis=1), axis=0)
    return B

def electricity_ratio(dt, sf, af):
    # Calculating Efficient Electricity Usage Ratio for an Alternative and Scenario
    rf = pd.DataFrame()

    for i in range(1, af + 1):
        fl = dt[(dt['Scenario'] == sf) & (dt['Alternative'] == i)]
        rf.loc[0, i] = fl['Weighted Efficiency Ratio'].sum()

    A = (np.power(10, rf)).rdiv(1)
    N = A.div(A.sum(axis=1), axis=0)
    return N


def electricity_total(dt, sf, af):
    # Calculating the total Electricity Purchased for an Alternative and Scenario
    rf = pd.DataFrame()
    for i in range(1, af + 1):
        fl = dt[(dt['Scenario'] == sf) & (dt['Alternative'] == i)]
        rf.loc[0, i] = fl['Electricity Purchased'].sum()

    A = rf.rdiv(1)
    N = A.div(A.sum(axis=1), axis=0)
    return N


def electricity_related(dt, sf, af):
    # Calculating Efficient Electricity Usage for all Alternatives
    A = electricity_ratio(dt, sf, af) + electricity_total(dt, sf, af)
    N = A.div(A.sum(axis=1), axis=0)
    return N


# Functions for aggregating results

def result_matrix(dt, sf, af):
    # Normalised results for indicators
    UR = usage_related(dt, sf, af)
    CR = capacity_related(dt, sf, af)
    N = fairness(dt, sf, af)
    FR = N.div(N.sum(axis=1), axis=0)
    RR = expansion_der(dt, sf, af)
    EF = electricity_related(dt, sf, af)
    rf = pd.concat([UR, CR, FR, RR, EF], ignore_index=True)
    return addnames(rf.T).T


def end_result(dt, sf, af, weights):
    # Combining indicator results with criteria's weights to generate ranking
    N = result_matrix(dt, sf, af)

    for j in range(1, len(N.columns) + 1):
        N[j] = N[j] * weights.transpose().iloc[:, 0]

    R = N.sum()

    return R


def results(dt, af, weights):
    # Aggregating results for all scenarios
    S1 = end_result(dt, 1, af, weights)
    S2 = end_result(dt, 2, af, weights)
    S3 = end_result(dt, 3, af, weights)
    S4 = end_result(dt, 4, af, weights)

    S = pd.concat([S1, S2, S3, S4], axis=1)
    S.columns = ['Scenario 1', 'Scenario 2', 'Scenario 3', 'Scenario 4']

    return S



# Generating ranking of alternative for every expert
EW = addnames(pd.DataFrame({
    0: {0: 1/6, 1: 1/6, 2: 1/3, 3: 1/6, 4: 1/6}
}).T)
results_EW = results(df, a, EW)
results_DSO = results(df, a, get_relative_weights_dso())
results_Authority = results(df, a, get_relative_weights_authority())
results_Regulator = results(df, a, get_relative_weights_regulator())
results_Politics = results(df, a, get_relative_weights_politics())
results_Third = results(df, a, get_relative_weights_third())

results_dict = {
    "Equal Weights": results_EW,
    "Authority": results_Authority,
    "Politics": results_Politics,
    "DSO": results_DSO,
    "Regulator": results_Regulator,
    "Third": results_Third,
}
# reformat and save results
for scenario in ['Scenario 1', 'Scenario 2', 'Scenario 3', 'Scenario 4']:
    tmp = pd.DataFrame()
    for weighting in \
            ["Equal Weights", "Authority", "Politics", "Third", "DSO", "Regulator"]:
        tmp[weighting] = results_dict[weighting][scenario]
    tmp.to_csv(f"results/end_rating_{scenario}.csv")
