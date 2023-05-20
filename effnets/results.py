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
