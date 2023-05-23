import pandas as pd
import numpy as np


# Implementation of the indicators with functions


def get_peak_cost_ratio(dt, idx_scenario, nr_alternatives):
    """
    Calculating Peak Impact Cost Ratio for an Alternative and Scenario

    :param dt: pd.DataFrame
        input data
    :param idx_scenario: int
        scenario to be analysed
    :param nr_alternatives: int
        total number of alternatives
    :return:
    """
    # calculate peak ratio, Eq. (4)
    dt['Peak Ratio'] = dt['Peak Share'] / dt['Cost Share']

    # calculate weighted peak ratio, Eq. (5)
    dt['Weighted Peak Ratio'] = (np.log10(dt['Peak Ratio']) * dt['Group Share']).abs()
    auxiliary_a = pd.DataFrame()
    for alternative in range(1, nr_alternatives + 1):
        tmp = dt[(dt['Scenario'] == idx_scenario) & (dt['Alternative'] == alternative)]
        auxiliary_a.loc[0, alternative] = tmp['Weighted Peak Ratio'].sum()

    # normalise such that values lie between 0 and 1, Eq. (6)
    peak_cost_ratio = (np.power(10, -auxiliary_a))

    # normalise to sum 1, Eq. (7) Todo: overthink if this makes sense
    rated_peak_cost_ratio = peak_cost_ratio.div(peak_cost_ratio.sum(axis=1), axis=0)
    return rated_peak_cost_ratio


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
    # calculate simultaneous power peaks, Eq. (8)
    simultaneous_peaks = pd.DataFrame()
    for alternative in range(1, nr_alternatives + 1):
        tmp = dt[(dt['Scenario'] == idx_scenario) & (dt['Alternative'] == alternative)]
        simultaneous_peaks.loc[0, alternative] = tmp['Simultaneous Peak'].sum()
    simultaneous_peaks_reciprocal = simultaneous_peaks.rdiv(1)
    rated_simultaneous_peaks = simultaneous_peaks_reciprocal.div(
        simultaneous_peaks_reciprocal.sum(axis=1), axis=0) # Todo: change to max? Or have relative to minimum possible value, i.e. flat consumption?
    return rated_simultaneous_peaks


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
        get_peak_cost_ratio(dt, idx_scenario, nr_alternatives) + \
        get_peak_total(dt, idx_scenario, nr_alternatives)
    # Todo: rating necessary? Divide by 2 instead?
    rated_reflection_usage_related = \
        reflection_usage_related.div(reflection_usage_related.sum(axis=1), axis=0)
    return rated_reflection_usage_related


def get_capacity_cost_ratio(dt, idx_scenario, nr_alternatives):
    """
    Calculating Contracted Capacity-Cost Ratio for an Alternative and Scenario

    :param dt: pd.DataFrame
        input data
    :param idx_scenario: int
        scenario to be analysed
    :param nr_alternatives: int
        total number of alternatives
    :return:
    """
    # calculate capacity ratio, Eq. (10)
    dt['Capacity Ratio'] = dt['Capacity Share'] / dt['Cost Share']

    # Calculate weighted capacity ratio, Eq. (13)
    dt['Weighted Capacity Ratio'] = \
        (np.log10(dt['Capacity Ratio']) * dt['Group Share']).abs()
    auxiliary_b = pd.DataFrame()
    for alternative in range(1, nr_alternatives + 1):
        tmp = dt[(dt['Scenario'] == idx_scenario) & (dt['Alternative'] == alternative)]
        auxiliary_b.loc[0, alternative] = tmp['Weighted Capacity Ratio'].sum()

    # normalise such that values lie between 0 and 1, Eq. (12)
    capacity_cost_ratio = (np.power(10, -auxiliary_b))

    # rate values, Eq. (14) Todo: overthink
    rated_capacity_cost_ratio = \
        capacity_cost_ratio.div(capacity_cost_ratio.sum(axis=1), axis=0)
    return rated_capacity_cost_ratio


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
    # calculate contracted capacity, Eq. (15)
    contracted_capacity = pd.DataFrame()
    for alternative in range(1, nr_alternatives + 1):
        tmp = dt[(dt['Scenario'] == idx_scenario) & (dt['Alternative'] == alternative)]
        contracted_capacity.loc[0, alternative] = tmp['Contracted Capacity'].sum()
    contracted_capacity_reciprocal = contracted_capacity.rdiv(1)
    rated_contracted_capacity = contracted_capacity_reciprocal.div(
        contracted_capacity_reciprocal.sum(axis=1), axis=0) # Todo: overthink, use theoretical minimum and maximum?
    return rated_contracted_capacity


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
        get_capacity_cost_ratio(dt, idx_scenario, nr_alternatives) + \
        get_capacity_total(dt, idx_scenario, nr_alternatives)
    # Todo: necessary? Divide by 2 instead?
    rated_reflection_capacity_related = reflection_capacity_related.div(
        reflection_capacity_related.sum(axis=1), axis=0)
    return rated_reflection_capacity_related


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
    dt['Relative Cost Share'] = dt['Cost Share'] / dt['Energy Share']
    # get base value for inflexible consumer group under energy based tariff
    dt_inflex_base = \
        dt[(dt['Scenario'] == 1) & (dt['Alternative'] == 1) &
           (dt['Customer Group'] == 1)]
    cost_share_inflex_base = dt_inflex_base.loc[0, 'Relative Cost Share']

    # Calculating Fairness and Customer Acceptance Ratio
    dt_inflex = dt[(dt['Customer Group'] == 1)].copy()
    dt_inflex['Fairness'] = cost_share_inflex_base / dt_inflex['Relative Cost Share']

    fairness = pd.DataFrame()

    for alternative in range(1, nr_alternatives + 1):
        tmp = dt_inflex[(dt_inflex['Scenario'] == idx_scenario) & (dt_inflex['Alternative'] == alternative)]
        fairness.loc[0, alternative] = tmp['Fairness'].values[0]
    # normalise_results, Eq. (20) - Todo: necessary?
    rated_fairness = fairness.div(fairness.sum(axis=1), axis=0)
    return rated_fairness


def get_pv_cost_ratio(dt, idx_scenario, nr_alternatives):
    """
    Do PV Owners pay more or less under a given tariff than under a volumetric tariff
    (relative to their purchased electricity share)

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

    # Calculating the PV Cost Ratio under given alternatives, Eq. (26)
    dt_pv_owners = dt[(dt['Customer Group'] == 2)].copy()
    dt_pv_owners['PV Cost Ratio'] = \
        cost_share_pv_owner_base / dt_pv_owners['Relative Cost Share']
    pv_cost_ratio = pd.DataFrame()
    for alternative in range(1, nr_alternatives + 1):
        tmp = dt_pv_owners[(dt_pv_owners['Scenario'] == idx_scenario) &
                           (dt_pv_owners['Alternative'] == alternative)]
        pv_cost_ratio.loc[0, alternative] = tmp['PV Cost Ratio'].values[0]

    # normalise pv-cost-ratio, Eq. (27) - Todo: necessary?
    rated_pv_cost_ratio = pv_cost_ratio.div(pv_cost_ratio.sum(axis=1), axis=0)
    return rated_pv_cost_ratio


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
    dt_pv_rentability = [[1.162, 1.0133, 1.0053, 1]] # Determined based on example consumer profiles Todo: move to input data?
    pv_rentability = pd.DataFrame(dt_pv_rentability, columns=[1, 2, 3, 4])
    # normalise PV rentability, Eq. (25) - Todo: necessary?
    rated_pv_rentability = pv_rentability.div(pv_rentability.sum(axis=1), axis=0)
    return rated_pv_rentability


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
    pv_cost_ratio = get_pv_cost_ratio(dt, idx_scenario, nr_alternatives)
    pv_rentability = get_pv_rentability(dt, idx_scenario, nr_alternatives)
    # combine and normalise indicators, Eq. (28)
    expansion_der = pv_cost_ratio + pv_rentability
    rated_expansion_der = expansion_der.div(expansion_der.sum(axis=1), axis=0)
    return rated_expansion_der


def get_electricity_cost_ratio(dt, idx_scenario, nr_alternatives):
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
    # get electricity cost ratio, Eq. (29)
    dt['Energy Ratio'] = dt['Energy Share'] / dt['Cost Share']

    # get auxiliary variable, Eq. (31)
    dt['Weighted Efficiency Ratio'] = \
        (np.log10(dt['Energy Ratio']) * dt['Group Share']).abs()
    auxiliary_c = pd.DataFrame()
    for alternative in range(1, nr_alternatives + 1):
        tmp = dt[(dt['Scenario'] == idx_scenario) & (dt['Alternative'] == alternative)]
        auxiliary_c.loc[0, alternative] = tmp['Weighted Efficiency Ratio'].sum()

    # get electricity cost ratio, Eq. (30)
    electricity_cost_ratio = (np.power(10, -auxiliary_c))
    # normalise electricity cost ratio, Eq. (32) - Todo: necessary?
    rated_electricity_cost_ratio = \
        electricity_cost_ratio.div(electricity_cost_ratio.sum(axis=1), axis=0)
    return rated_electricity_cost_ratio


def electricity_total(dt, idx_scenario, nr_alternatives):
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
    # get reduction of purchased electricity, Eq. (33) - Todo: overthink
    purchased_electricity = pd.DataFrame()
    for alternative in range(1, nr_alternatives + 1):
        tmp = dt[(dt['Scenario'] == idx_scenario) & (dt['Alternative'] == alternative)]
        purchased_electricity.loc[0, alternative] = tmp['Electricity Purchased'].sum()
    purchased_electricity_reciprocal = purchased_electricity.rdiv(1)
    rated_purchased_electricity = purchased_electricity_reciprocal.div(
        purchased_electricity_reciprocal.sum(axis=1), axis=0) # Todo: necessary?
    return rated_purchased_electricity


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
    efficient_electricity_usage = \
        get_electricity_cost_ratio(dt, idx_scenario, nr_alternatives) + \
        electricity_total(dt, idx_scenario, nr_alternatives)
    rated_efficient_electricity_usage = efficient_electricity_usage.div(
        efficient_electricity_usage.sum(axis=1), axis=0) # Todo: necessary?
    return rated_efficient_electricity_usage
