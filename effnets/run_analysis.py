import pandas as pd
import numpy as np

from data.expert_weighting import expert_pairwise_comparison_dict
from weights import get_relative_weights_stakeholder, addnames
from indicators import pvcost_ratio, fairness
from results import results, r_matrix


# Number of scenarios
s = 4
# Number of alternatives
a = 4
# Number of criteria
c = 5

# Import input data from simulated network
data = pd.read_excel(r'data/inputdata.xlsx',
                     sheet_name='Input')
df = pd.DataFrame(
    data, columns=['Scenario', 'Alternative', 'Customer Group', 'Group Share',
                   'Cost Share', 'Peak Share', 'Capacity Share', 'Energy Share',
                   'Electricity Purchased', 'Simultaneous Peak', 'Contracted Capacity',
                   'Local Peak'])

# Auxiliary values
df['Relative Cost Share'] = df['Cost Share'] / df['Energy Share']
df['Peak Ratio'] = df['Peak Share']/df['Cost Share']
df['Capacity Ratio'] = df['Capacity Share']/df['Cost Share']
df['Energy Ratio'] = df['Energy Share']/df['Cost Share']

df['Weighted Peak Ratio'] = (np.log10(df['Peak Ratio']) * df['Group Share']).abs()
df['Weighted Capacity Ratio'] = \
    (np.log10(df['Capacity Ratio']) * df['Group Share']).abs()
df['Weighted Efficiency Ratio'] = \
    (np.log10(df['Energy Ratio']) * df['Group Share']).abs()

# Generating ranking of alternative for every expert
equal_weights = addnames(pd.DataFrame({
    0: {0: 1/6, 1: 1/6, 2: 1/3, 3: 1/6, 4: 1/6}
}).T)
results_EW = results(df, a, equal_weights)
results_dict = {
    "Equal Weights": results_EW}
# get results with expert weighting
expert_weights = expert_pairwise_comparison_dict()
for expert in ["Authority", "Politics", "DSO", "Regulator", "Third Party"]:
    results_dict[expert] = results(df, a, get_relative_weights_stakeholder(
        expert_weights[expert], expert
    ))

# reformat and save results
for scenario in ['Scenario 1', 'Scenario 2', 'Scenario 3', 'Scenario 4']:
    tmp = pd.DataFrame()
    for weighting in ["Equal Weights", "Authority", "Politics", "Third Party", "DSO",
                      "Regulator"]:
        tmp[weighting] = results_dict[weighting][scenario]
    tmp.to_csv(f"results/end_rating_{scenario}.csv")


r = pd.concat([r_matrix(df, 1, a), r_matrix(df, 2, a),
               r_matrix(df, 3, a), r_matrix(df, 4, a)])
r.to_excel(r'results/resultmatrix.xlsx')

f = pd.concat([fairness(df, 1, a), fairness(df, 2, a),
               fairness(df, 3, a), fairness(df, 4, a)])
f['Scenario'] = [1, 2, 3, 4]
f.set_index('Scenario', inplace = True)
f.to_excel(r'results/fairness.xlsx')

p = pd.concat([pvcost_ratio(df, 1, a), pvcost_ratio(df, 2, a),
               pvcost_ratio(df, 3, a), pvcost_ratio(df, 4, a)])
p['Scenario'] = [1, 2, 3, 4]
p.set_index('Scenario', inplace = True)
p.to_excel(r'results/pvrentability.xlsx')

df.to_excel(r'results/df.xlsx')
total_weights = \
        pd.concat([get_relative_weights_stakeholder(expert_weights["DSO"], "DSO"),
                   get_relative_weights_stakeholder(expert_weights["Authority"],
                                                    "Authority"),
                   get_relative_weights_stakeholder(expert_weights["Regulator"],
                                                    "Regulator"),
                   get_relative_weights_stakeholder(expert_weights["Politics"],
                                                    "Politics"),
                   get_relative_weights_stakeholder(expert_weights["Third Party"],
                                                    "Third Party")])
total_weights.to_excel(r'results/weighting.xlsx')

e = pd.concat([results_dict["DSO"],
               results_dict["Authority"],
               results_dict["Regulator"],
               results_dict["Politics"],
               results_dict["Third Party"]])
e.to_excel(r'results/endresults.xlsx')

# Calculations - LEVEL ALTERNATIVES (AGGREGATION OF CUSTOMER GROUPS) -
# for additional charts
rf = pd.DataFrame()
for i in range(1, s+1):
    for j in range(1, a+1):
        rf.loc[i*a-a+j, 'Scenario'] = i
        rf.loc[i*a-a+j, 'Alternative'] = j
        fl = df[(df['Scenario'] == i) & (df['Alternative'] == j)]
        rf.loc[i*a-a+j, 'Aggregated Peak'] = fl['Simultaneous Peak'].sum()
        rf.loc[i*a-a+j, 'Contracted Capacity'] = fl['Contracted Capacity'].sum()
        rf.loc[i*a-a+j, 'Electricity Purchased'] = fl['Electricity Purchased'].sum()

rf.to_excel(r'results/values.xlsx')
