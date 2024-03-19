import pandas as pd
import os

from data.expert_weighting import expert_pairwise_comparison_dict
from data.data_preparation import import_data
from indicators import add_names_criteria
from weights import get_relative_weights_stakeholder
from results import get_results, get_performance_indicators_scenario_with_names

# create results directory if it does not already exist
os.makedirs("results", exist_ok=True)

# Number of scenarios
nr_scenarios = 4
scenario_names = ['Scenario 1', 'Scenario 2', 'Scenario 3', 'Scenario 4']
# Number of alternatives
nr_alternatives = 4
alternative_names = ['Volumetric Tariff', 'Monthly Power Peak',
                     'Yearly Power Peak', 'Capacity Tariff']
# Number of criteria
nr_criteria = 5
# Experts
experts = ["Authority", "Politics", "Third Party", "DSO", "Regulator"]

# Import input data from simulated network
dt = import_data()

# Generating ranking of alternative for every expert
equal_weights = add_names_criteria(pd.DataFrame({
    0: {0: 1/3, 1: 1/3, 2: 1/6, 3: 1/6}
}).T)
results_EW = \
    get_results(dt, nr_scenarios, nr_alternatives, equal_weights, scenario_names)
results_dict = {
    "Equal Weights": results_EW}
# get results with expert weighting
expert_weights = expert_pairwise_comparison_dict()
for expert in experts:
    results_dict[expert] = get_results(
        dt, nr_scenarios, nr_alternatives, get_relative_weights_stakeholder(
            expert_weights[expert], expert
        ), scenario_names)

# reformat and save results
results_tmp = []
for scenario in scenario_names:
    tmp = pd.DataFrame()
    for weighting in ["Equal Weights"] + experts:
        tmp[weighting] = results_dict[weighting][scenario]
    tmp["Scenario"] = scenario
    tmp["Network Tariff"] = alternative_names
    results_tmp.append(tmp)
pd.concat(results_tmp, ignore_index=True).to_csv(f"results/end_rating.csv")


results_matrix = pd.concat([
    get_performance_indicators_scenario_with_names(
        dt, i+1, nr_alternatives, alternative_names)
    for i in range(nr_scenarios)
])
results_matrix.to_csv(r'results/result_matrix.csv')

# Auxiliary values

total_weights = \
        pd.concat([get_relative_weights_stakeholder(expert_weights[expert], expert)
                   for expert in experts])
total_weights.to_csv(r'results/weighting.csv')

print("Success")
