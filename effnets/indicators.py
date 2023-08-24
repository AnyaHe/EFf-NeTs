import pandas as pd
import numpy as np


# Implementation of the indicators with functions


def get_relative_reduction(dt, idx_scenario, nr_alternatives, parameter):
    """
    Calculating reduction indicator of absolute value of <parameter> (e.g. 'Simultaneous
    Peak'). The indicator is thereby calculated relative to the reference alternative
    (1), here the volumetric tariff. If the parameter value is the same as for the
    volumetric tariff, the indicator will have a value of 0.5, if the parameter is
    reduced by 50%, the indicator will be 1.0, if it is increased by 50%, it will be 0.
    Negative values indicate an increase >50%, positive values can reach up to 1.5, if
    the parameter value is reduced to 0.

    :param dt: pd.DataFrame
        input data
    :param idx_scenario: int
        scenario to be analysed
    :param nr_alternatives: int
        total number of alternatives
    :param parameter: str
        total number of alternatives
    :return:
    """
    # get reference peak for volumetric tariff
    reference = dt[(dt['Scenario'] == idx_scenario) &
                   (dt['Alternative'] == 1)][parameter].sum()
    # calculate simultaneous power peaks
    parameter_values = pd.DataFrame()
    for alternative in range(1, nr_alternatives + 1):
        tmp = dt[(dt['Scenario'] == idx_scenario) & (dt['Alternative'] == alternative)]
        parameter_values.loc[0, alternative] = tmp[parameter].sum()
    # calculate relative reduction, e.g. Eq. (3)
    reduction_indicator = 1.5 - parameter_values.divide(reference)
    return reduction_indicator


def get_reduction_of_usage_related_costs(dt, idx_scenario, nr_alternatives):
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
        get_relative_reduction(dt, idx_scenario, nr_alternatives, 'Simultaneous Peak')
    return reflection_usage_related


def get_reduction_of_capacity_related_costs(dt, idx_scenario, nr_alternatives):
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
        get_relative_reduction(dt, idx_scenario, nr_alternatives, "Contracted Capacity")
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
    cost_contribution_cr, cost_contribution_ur = \
        get_share_usage_and_capacity_related_costs()
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
        slope.loc[0, alternative] = min([abs(beta_1), abs(1/beta_1)])
    return correlation.multiply(slope)


def get_share_usage_and_capacity_related_costs():
    # calculate division into usage- and capacity-related costs
    cost_contribution_ur = pd.read_csv("data/cost_contribution_ur.csv", index_col=0,
                                       dtype={0: int})
    cost_contribution_ur.columns = cost_contribution_ur.columns.astype(int)
    cost_contribution_cr = 1 - cost_contribution_ur
    return cost_contribution_cr, cost_contribution_ur


def get_efficient_grid(dt, idx_scenario, nr_alternatives):
    """
    Get indicator for efficient grid

    :param dt: pd.DataFrame
        input data
    :param idx_scenario: int
        scenario to be analysed
    :param nr_alternatives: int
        total number of alternatives
    :return:
    """
    cost_contribution_cr, cost_contribution_ur = \
        get_share_usage_and_capacity_related_costs()
    weight_ur = cost_contribution_ur.loc[idx_scenario]
    weight_cr = cost_contribution_cr.loc[idx_scenario]
    reflection_of_costs = get_reflection_of_costs(dt, idx_scenario, nr_alternatives)
    reduction_of_usage_related_costs = \
        get_reduction_of_usage_related_costs(dt, idx_scenario, nr_alternatives)
    reduction_of_capacity_related_costs = \
        get_reduction_of_capacity_related_costs(dt, idx_scenario, nr_alternatives)
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
        tmp = dt_inflex[(dt_inflex['Scenario'] == idx_scenario) &
                        (dt_inflex['Alternative'] == alternative)]
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


def get_expansion_der(dt, idx_scenario, nr_alternatives):
    """
    How much can consumers not owning a PV system yet save by purchasing one?

    :param dt: pd.DataFrame
        input data
    :param idx_scenario: int
        scenario to be analysed
    :param nr_alternatives: int
        total number of alternatives
    :return:
    """
    # read data
    dt_pv_cost_change = pd.read_csv("data/pv_cost_reduction.csv", index_col=0).rename(
        columns={"VT": 1, "MPT": 2, "YPT": 3, "CT": 4}
    )
    # get customer shares of non-PV-owners
    cg1_share = dt.loc[(dt.Scenario == idx_scenario)&(dt["Customer Group"] == 1),
                       "Group Share"].unique()[0]
    cg2_share = dt.loc[(dt.Scenario == idx_scenario) & (dt["Customer Group"] == 3),
                       "Group Share"].unique()[0]
    cu = cg1_share + cg2_share
    # get PV rentability, Eq. (21)-(24)
    pv_cost_change = cg1_share/cu * (0.5 * dt_pv_cost_change.loc["PV"] +
                                     0.5 * dt_pv_cost_change.loc["PV_BESS"]) + \
                     cg2_share/cu * (0.5 * dt_pv_cost_change.loc["EV_PV"] +
                                     0.5 * dt_pv_cost_change.loc["EV_PV_BESS"])
    df_pv_cost_change = pd.DataFrame(index=[1, 2, 3, 4])
    df_pv_cost_change[0] = pv_cost_change
    # normalise PV rentability, Eq. (25) - Todo: necessary?
    pv_rentability = 1.5 - df_pv_cost_change.T
    return pv_rentability


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
        slope.loc[0, alternative] = min([abs(beta_3), abs(1/beta_3)])
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
