# libraries
import numpy as np
import matplotlib.pyplot as plt
from indicators import *
from weights import *


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
        pd.concat([get_relative_weights_dso(),
                   get_relative_weights_authority(),
                   get_relative_weights_regulator(),
                   get_relative_weights_politics(),
                   get_relative_weights_third()])
total_weights.to_excel(r'results/weighting.xlsx')

e = pd.concat([results_DSO, results_Authority, results_Regulator,
               results_Politics, results_Third])
e.to_excel(r'results/endresults.xlsx')

# Calculations - LEVEL ALTERNATIVES (AGGREGATION OF CUSTOMER GROUPS) - for additional charts
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
