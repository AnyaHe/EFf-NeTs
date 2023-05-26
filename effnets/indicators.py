import pandas as pd
import numpy as np


# Implementation of the indicators with functions


def get_peak_total(dt, idx_scenario, nr_alternatives):
    """
    Calculating Simultaneous Peak for an Alternative and Scenario

    :param dt: pd.DataFrame
        input data
    :param idx_scenario: int
        scenario to be analysed
    :param nr_alternatives: int
        total number of alternatives
    :return:
    """
    # choose relevant column in input data
    res_col = 'Simultaneous Peak'
    # get reference peak for volumetric tariff
    reference_peak = dt[(dt['Scenario'] == idx_scenario) &
                        (dt['Alternative'] == 1)][res_col].sum()
    # calculate simultaneous power peaks
    simultaneous_peaks = pd.DataFrame()
    for alternative in range(1, nr_alternatives + 1):
        tmp = dt[(dt['Scenario'] == idx_scenario) & (dt['Alternative'] == alternative)]
        simultaneous_peaks.loc[0, alternative] = tmp[res_col].sum()
    # calculate peak reduction, Eq. (3)
    peak_reduction = 1.5 - simultaneous_peaks.divide(reference_peak)
    return peak_reduction


def get_reflection_of_usage_related_costs(dt, idx_scenario, nr_alternatives):
    """
    Calculating Usage (Peak) Related Distribution Factor for All Alternatives in given
    Scenario

    :param dt: pd.DataFrame
        input data
    :param idx_scenario: int
        scenario to be analysed
    :param nr_alternatives: int
        total number of alternatives
    :return:
    """
    # rated reflection of usage related costs, Eq. (9)
    reflection_usage_related = \
        get_peak_total(dt, idx_scenario, nr_alternatives)
    return reflection_usage_related


def get_capacity_total(dt, idx_scenario, nr_alternatives):
    """
    Calculating the total Contracted Capacity for an Alternative and Scenario

    :param dt: pd.DataFrame
        input data
    :param idx_scenario: int
        scenario to be analysed
    :param nr_alternatives: int
        total number of alternatives
    :return:
    """
    # get reference contracted capacity for volumetric tariff
    reference_capacity = dt[(dt['Scenario'] == idx_scenario) &
                        (dt['Alternative'] == 1)]['Contracted Capacity'].sum()
    # calculate contracted capacity
    contracted_capacity = pd.DataFrame()
    for alternative in range(1, nr_alternatives + 1):
        tmp = dt[(dt['Scenario'] == idx_scenario) & (dt['Alternative'] == alternative)]
        contracted_capacity.loc[0, alternative] = tmp['Contracted Capacity'].sum()
    # calculate peak reduction, Eq. (4)
    capacity_reduction = 1.5 - contracted_capacity.divide(reference_capacity)
    return capacity_reduction


def get_reflection_of_capacity_related_costs(dt, idx_scenario, nr_alternatives):
    """
    Calculating Capacity Related Distribution Factor for All Alternatives

    :param dt: pd.DataFrame
        input data
    :param idx_scenario: int
        scenario to be analysed
    :param nr_alternatives: int
        total number of alternatives
    :return:
    """
    # reflection of capacity related costs, Eq. (16)
    reflection_capacity_related = \
        get_capacity_total(dt, idx_scenario, nr_alternatives)
    return reflection_capacity_related


def get_reflection_of_costs(dt, idx_scenario, nr_alternatives):
    """
    Calculating Reflection of Costs for All Alternatives

    :param dt: pd.DataFrame
        input data
    :param idx_scenario: int
        scenario to be analysed
    :param nr_alternatives: int
        total number of alternatives
    :return:
    """
    # calculate division into usage- and capacity-related costs
    cost_contribution_ur = pd.read_csv("data/cost_contribution_ur.csv", index_col=0,
                                       dtype={0: int})
    cost_contribution_ur.columns = cost_contribution_ur.columns.astype(int)
    cost_contribution_cr = 1 - cost_contribution_ur
    # calculate share on aggregated peak
    correlation = pd.DataFrame()
    slope = pd.DataFrame()
    for alternative in range(1, nr_alternatives + 1):
        tmp = dt[(dt['Scenario'] == idx_scenario) & (dt['Alternative'] == alternative)]
        cost_share = tmp["Cost Share"].values
        peak_share = tmp['Peak Share'].values
        capacity_share = tmp['Capacity Share'].values
        # scale to costs, Eq. (8)
        peak_share_scaled = \
            cost_contribution_ur.loc[idx_scenario, alternative] * peak_share
        # scale to costs, Eq. (9)
        capacity_share_scaled = \
            cost_contribution_cr.loc[idx_scenario, alternative] * capacity_share
        # extract correlation, Eq.()
        correlation.loc[0, alternative] = \
            np.corrcoef(cost_share, peak_share_scaled + capacity_share_scaled)[0, 1]
        # extract slope, Eq. () Todo: is a slope > 1 bad? Punishment too high then
        beta_1 = np.polyfit(cost_share, peak_share_scaled + capacity_share_scaled, 1)[0]
        slope.loc[0, alternative] = 1 - abs(1-beta_1)
    return correlation.multiply(slope)


def get_efficient_grid(dt, idx_scenario, nr_alternatives, weight_ur=0.5, weight_cr=0.5):
    """
    Get indicator for efficient grid

    :param dt: pd.DataFrame
        input data
    :param idx_scenario: int
        scenario to be analysed
    :param nr_alternatives: int
        total number of alternatives
    :param weight_ur: float
        relative weight for reflection of usage-related costs, weight_ur+weight_cr=1
    :param weight_cr: float
        relative weight for reflection of capacity-related, weight_ur+weight_cr=1
    :return:
    """
    reflection_of_costs = get_reflection_of_costs(dt, idx_scenario, nr_alternatives)
    reduction_of_usage_related_costs = \
        get_reflection_of_usage_related_costs(dt, idx_scenario, nr_alternatives)
    reduction_of_capacity_related_costs = \
        get_reflection_of_capacity_related_costs(dt, idx_scenario, nr_alternatives)
    efficient_grid = \
        0.5 * (reflection_of_costs + weight_ur * reduction_of_usage_related_costs +
               weight_cr * reduction_of_capacity_related_costs)
    return efficient_grid


def get_fairness(dt, idx_scenario, nr_alternatives):
    """
    Relative Cost Share of Inflexible Customers (Reference Value)
    Todo: overthink this value, should it really be coupled to energy utilisation? Or just share from scenario? Or use values from cost reflection?

    :param dt: pd.DataFrame
        input data
    :param idx_scenario: int
        scenario to be analysed
    :param nr_alternatives: int
        total number of alternatives
    :return:
    """
    # get relative cost share, Eq. (18)
    dt['Relative Cost Share'] = dt['Cost Share'] / dt['Group Share']
    # get base value for inflexible consumer group under energy based tariff
    dt_inflex_base = \
        dt[(dt['Scenario'] == 1) & (dt['Alternative'] == 1) &
           (dt['Customer Group'] == 1)]
    cost_share_inflex_base = dt_inflex_base.loc[0, 'Relative Cost Share']

    # Calculating Fairness and Customer Acceptance Ratio
    dt_inflex = dt[(dt['Customer Group'] == 1)].copy()
    dt_inflex['Fairness'] = \
        1.5 - dt_inflex['Relative Cost Share'] / cost_share_inflex_base

    fairness = pd.DataFrame()

    for alternative in range(1, nr_alternatives + 1):
        tmp = dt_inflex[(dt_inflex['Scenario'] == idx_scenario) & (dt_inflex['Alternative'] == alternative)]
        fairness.loc[0, alternative] = tmp['Fairness'].values[0]
    return fairness


def get_cost_change_pv(dt, idx_scenario, nr_alternatives):
    """
    Do PV Owners pay more or less under a given tariff than under a volumetric tariff
    (relative to their purchased electricity share)
    # Todo: include other consumer groups as well? Battery might be more helpful

    :param dt: pd.DataFrame
        input data
    :param idx_scenario: int
        scenario to be analysed
    :param nr_alternatives: int
        total number of alternatives
    :return:
    """
    # Relative Cost Share of Customer Group 2 (Reference Value)
    dt_pv_owners_base = dt[(dt['Scenario'] == idx_scenario) &
                           (dt['Alternative'] == 1) & (dt['Customer Group'] == 2)]
    cost_share_pv_owner_base = dt_pv_owners_base['Relative Cost Share'].values[0]
    df_inflex_base = dt[(dt['Scenario'] == idx_scenario) &
                        (dt['Alternative'] == 1) & (dt['Customer Group'] == 1)]
    cost_share_inflex_base = df_inflex_base['Relative Cost Share'].values[0]
    relative_costs_base = cost_share_pv_owner_base/cost_share_inflex_base

    # Calculating the PV Cost Ratio under given alternatives, Eq. (26)
    dt_pv_owners = dt[(dt['Customer Group'] == 2)].copy()
    dt_inflex = dt[(dt['Customer Group'] == 1)].copy()
    dt_pv_owners['PV Cost Ratio'] = \
        dt_pv_owners['Relative Cost Share'] / dt_inflex['Relative Cost Share'].values / \
        relative_costs_base
    pv_cost_ratio = pd.DataFrame()
    for alternative in range(1, nr_alternatives + 1):
        tmp = dt_pv_owners[(dt_pv_owners['Scenario'] == idx_scenario) &
                           (dt_pv_owners['Alternative'] == alternative)]
        pv_cost_ratio.loc[0, alternative] = 1.5 - tmp['PV Cost Ratio'].values[0]
    return pv_cost_ratio


def get_pv_rentability(dt, idx_scenario, nr_alternatives):
    """
    How much can inflexible consumers save by purchasing a PV System?

    :param dt: pd.DataFrame
        input data
    :param idx_scenario: int
        scenario to be analysed
    :param nr_alternatives: int
        total number of alternatives
    :return:
    """
    # get PV rentability, Eq. (21)-(24)
    dt_pv_cost_change = [[1.162, 1.0133, 1.0053, 1]] # Determined based on example consumer profiles Todo: move to input data?
    pv_cost_change = pd.DataFrame(dt_pv_cost_change, columns=[1, 2, 3, 4])
    # normalise PV rentability, Eq. (25) - Todo: necessary?
    pv_rentability = 1.5 - pv_cost_change.rdiv(1)
    return pv_rentability


def get_expansion_der(dt, idx_scenario, nr_alternatives):
    """
    Calculating indicator for criterion of expanding DER for All Alternatives

    :param dt: pd.DataFrame
        input data
    :param idx_scenario: int
        scenario to be analysed
    :param nr_alternatives: int
        total number of alternatives
    :return:
    """
    pv_cost_ratio = get_cost_change_pv(dt, idx_scenario, nr_alternatives)
    pv_rentability = get_pv_rentability(dt, idx_scenario, nr_alternatives)
    # combine and normalise indicators, Eq. (28)
    expansion_der = (pv_cost_ratio + pv_rentability)/2
    return expansion_der


def get_reflection_of_electricity(dt, idx_scenario, nr_alternatives):
    """
    Calculating Efficient Electricity Usage Ratio for an Alternative and Scenario

    :param dt: pd.DataFrame
        input data
    :param idx_scenario: int
        scenario to be analysed
    :param nr_alternatives: int
        total number of alternatives
    :return:
    """
    # calculate correlation and slope between cost share and energy share
    correlation = pd.DataFrame()
    slope = pd.DataFrame()
    for alternative in range(1, nr_alternatives + 1):
        tmp = dt[(dt['Scenario'] == idx_scenario) & (dt['Alternative'] == alternative)]
        cost_share = tmp["Cost Share"].values
        energy_share = tmp['Energy Share'].values
        # extract correlation, Eq.()
        correlation.loc[0, alternative] = \
            np.corrcoef(cost_share, energy_share)[0, 1]
        # extract slope, Eq. () Todo: is a slope > 1 bad? Punishment too high then
        beta_3 = np.polyfit(cost_share, energy_share, 1)[0]
        slope.loc[0, alternative] = 1 - abs(1 - beta_3)
    return correlation.multiply(slope)


def get_reduction_of_purchased_electricity(dt, idx_scenario, nr_alternatives):
    """
    Calculating the total Electricity Purchased for an Alternative and Scenario

    :param dt: pd.DataFrame
        input data
    :param idx_scenario: int
        scenario to be analysed
    :param nr_alternatives: int
        total number of alternatives
    :return:
    """
    # get base value for volumetric tariff
    dt_base = dt[(dt['Scenario'] == idx_scenario) & (dt['Alternative'] == 1)]
    purchased_electricity_base = dt_base["Electricity Purchased"].sum()
    # get reduction of purchased electricity, Eq. (33) - Todo: overthink
    purchased_electricity = pd.DataFrame()
    for alternative in range(1, nr_alternatives + 1):
        tmp = dt[(dt['Scenario'] == idx_scenario) & (dt['Alternative'] == alternative)]
        purchased_electricity.loc[0, alternative] = \
            1.5 - tmp['Electricity Purchased'].sum() / purchased_electricity_base
    return purchased_electricity


def get_efficient_electricity_usage(dt, idx_scenario, nr_alternatives):
    """
    Calculating Efficient Electricity Usage for all Alternatives

    :param dt: pd.DataFrame
        input data
    :param idx_scenario: int
        scenario to be analysed
    :param nr_alternatives: int
        total number of alternatives
    :return:
    """
    # combine and normalise electricity cost ratio and reduction in purchased
    # electricity, Eq.(34)
    efficient_electricity_usage = 0.5 * (
            get_reflection_of_electricity(dt, idx_scenario, nr_alternatives) +
            get_reduction_of_purchased_electricity(dt, idx_scenario, nr_alternatives))
    return efficient_electricity_usage
