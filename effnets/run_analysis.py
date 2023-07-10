import pandas as pd
import numpy as np

from data.expert_weighting import expert_pairwise_comparison_dict
from weights import get_relative_weights_stakeholder, add_names_criteria
from indicators import get_cost_change_pv, get_fairness
from results import get_results, get_performance_indicators_scenario_with_names


# Number of scenarios
nr_scenarios = 4
# Number of alternatives
nr_alternatives = 4
# Number of criteria
nr_criteria = 5

# Import input data from simulated network
data = pd.read_excel(r'data/inputdata_new.xlsx',
                     sheet_name='Simulation_Analysis_Results')
rename_dict = {
    "Customer_Group": "Customer Group",
    "Group_Share": "Group Share",
    "Cost_share": "Cost Share",
    "Peak_share": "Peak Share",
    "Energy_share": "Energy Share",
    "Capacity_share": "Capacity Share",
    "Energiesumme": "Electricity Purchased",
    "AggregierteP": "Aggregated Peak",
    "AggregiertePglz": "Simultaneous Peak",
    "AggregierteCap": "Contracted Capacity",
    "Total_Losses": "Losses Share"
}
dt = data.rename(columns=rename_dict)

# Generating ranking of alternative for every expert
equal_weights = add_names_criteria(pd.DataFrame({
    0: {0: 1/3, 1: 1/3, 2: 1/6, 3: 1/6}
}).T)
results_EW = get_results(dt, nr_alternatives, equal_weights)
results_dict = {
    "Equal Weights": results_EW}
# get results with expert weighting
expert_weights = expert_pairwise_comparison_dict()
for expert in ["Authority", "Politics", "DSO", "Regulator", "Third Party"]:
    results_dict[expert] = get_results(
        dt, nr_alternatives, get_relative_weights_stakeholder(
            expert_weights[expert], expert
        ))

# reformat and save results
for scenario in ['Scenario 1', 'Scenario 2', 'Scenario 3', 'Scenario 4']:
    tmp = pd.DataFrame()
    for weighting in ["Equal Weights", "Authority", "Politics", "Third Party", "DSO",
                      "Regulator"]:
        tmp[weighting] = results_dict[weighting][scenario]
    tmp.to_csv(f"results/end_rating_{scenario}.csv")


results_matrix = pd.concat([
    get_performance_indicators_scenario_with_names(dt, 1, nr_alternatives),
    get_performance_indicators_scenario_with_names(dt, 2, nr_alternatives),
    get_performance_indicators_scenario_with_names(dt, 3, nr_alternatives),
    get_performance_indicators_scenario_with_names(dt, 4, nr_alternatives)])
results_matrix.to_excel(r'results/resultmatrix.xlsx')

fairness = pd.concat([
    get_fairness(dt, 1, nr_alternatives), get_fairness(dt, 2, nr_alternatives),
    get_fairness(dt, 3, nr_alternatives), get_fairness(dt, 4, nr_alternatives)])
fairness['Scenario'] = [1, 2, 3, 4]
fairness.set_index('Scenario', inplace = True)
fairness.to_excel(r'results/fairness.xlsx')

pv_rentability = pd.concat([get_cost_change_pv(dt, 1, nr_alternatives),
                            get_cost_change_pv(dt, 2, nr_alternatives),
                            get_cost_change_pv(dt, 3, nr_alternatives),
                            get_cost_change_pv(dt, 4, nr_alternatives)])
pv_rentability['Scenario'] = [1, 2, 3, 4]
pv_rentability.set_index('Scenario', inplace = True)
pv_rentability.to_excel(r'results/pvrentability.xlsx')

# Auxiliary values

dt.to_excel(r'results/df.xlsx')

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

end_results = pd.concat([results_dict["DSO"],
                         results_dict["Authority"],
                         results_dict["Regulator"],
                         results_dict["Politics"],
                         results_dict["Third Party"]])
end_results.to_excel(r'results/endresults.xlsx')

# Calculations - LEVEL ALTERNATIVES (AGGREGATION OF CUSTOMER GROUPS) -
# for additional charts
results_final = pd.DataFrame()
for scenario in range(1, nr_scenarios + 1):
    for alternative in range(1, nr_alternatives + 1):
        idx = (scenario - 1) * nr_alternatives + alternative
        results_final.loc[idx, 'Scenario'] = scenario
        results_final.loc[idx, 'Alternative'] = alternative
        tmp = dt[(dt['Scenario'] == scenario) & (dt['Alternative'] == alternative)]
        results_final.loc[idx, 'Aggregated Peak'] = tmp['Simultaneous Peak'].sum()
        results_final.loc[idx, 'Contracted Capacity'] = tmp['Contracted Capacity'].sum()
        results_final.loc[idx, 'Electricity Purchased'] = \
            tmp['Electricity Purchased'].sum()

results_final.to_excel(r'results/values.xlsx')
