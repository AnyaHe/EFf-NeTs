# Methods to provide certain input data
import pandas as pd


def determine_usage_and_capacity_related_cost_contributions():
    """
    Determine cost contribution of peaks and capacity contraction based on the
    assumption that a cost share from literature is achieved by the status quo
    (idx_scenario=1) with volumetric tariff (alternative=1)

    :return:
    """
    # calculate division into usage- and capacity-related costs
    ur_base = 0.41  # from Chanel and Limoges
    cr_base = 0.59  # from Chanel and Limoges
    # get data of base scenario
    data = pd.read_excel(r'inputdata.xlsx',
                         sheet_name='Input')
    dt = pd.DataFrame(
        data, columns=['Scenario', 'Alternative', 'Customer Group', 'Group Share',
                       'Cost Share', 'Peak Share', 'Capacity Share', 'Energy Share',
                       'Electricity Purchased', 'Simultaneous Peak',
                       'Contracted Capacity',
                       'Local Peak'])
    base_dt = dt[(dt['Scenario'] == 1) & (dt['Alternative'] == 1)]
    peak_base = base_dt['Simultaneous Peak'].sum()
    capacity_base = base_dt['Contracted Capacity'].sum()
    # get cost contribution of peaks and capacity
    cost_contribution_ur = pd.DataFrame()
    cost_contribution_cr = pd.DataFrame()
    for scenario in dt["Scenario"].unique():
        for alternative in dt["Alternative"].unique():
            # adapt to new alternative and scenario, Eq. (33)
            peak = dt[(dt['Scenario'] == scenario) &
                      (dt['Alternative'] == alternative)]['Simultaneous Peak'].sum()
            ur_tmp = ur_base * peak / peak_base
            # adapt to new alternative and scenario, Eq. (34)
            capacity = \
                dt[(dt['Scenario'] == scenario) &
                   (dt['Alternative'] == alternative)]['Contracted Capacity'].sum()
            cr_tmp = cr_base * capacity / capacity_base
            # normalise so sum is 1, Eq. (35)
            cost_contribution_ur.loc[scenario, alternative] = ur_tmp/(ur_tmp+cr_tmp)
            cost_contribution_cr.loc[scenario, alternative] = cr_tmp / (ur_tmp + cr_tmp)
    return cost_contribution_ur, cost_contribution_cr


if __name__ == "__main__":
    cost_contribution_ur, cost_contribution_cr = \
        determine_usage_and_capacity_related_cost_contributions()
    cost_contribution_ur.to_csv("cost_contribution_ur.csv")
