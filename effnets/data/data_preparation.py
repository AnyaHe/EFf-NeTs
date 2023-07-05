# Methods to provide certain input data
import pandas as pd
import os
from itertools import product


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


def get_profiles_of_different_consumer_groups(profiles_hh, profiles_pv,
                                              profiles_ev=None, profiles_bess=None):
    """
    Method to generate combined profiles with representative time series of households
    (hh), PV, BESS and EVs.

    :param profiles_hh:
    :param profiles_pv:
    :param profiles_ev:
    :param profiles_bess:
    :return:
    """
    def _get_combined_profiles(profiles_1, profiles_2):
        """
        Method to obtain combination of all profiles in profiles_1 with all profiles in
        profiles_2. The combined profiles will contain
        len(profiles_1.columns)*len(profiles_2.columns) columns.

        :param profiles_1: pd.DataFrame
            columns determine different profiles
        :param profiles_2: pd.DataFrame
            columns determine different profiles
        :return: pd.DataFrame()
        """
        combined_profiles = pd.concat(
            [profiles_1] * len(profiles_2.columns), axis=1)[profiles_1.columns] + \
            pd.concat([profiles_2] * len(profiles_1.columns), axis=1).values
        col_names = ["-".join(prod) for prod in list(product(profiles_1.columns,
                                                             profiles_2.columns))]
        combined_profiles.columns = col_names
        return combined_profiles

    # Todo: might not be necessary, if you just enter the profiles
    # Determine profiles HH with PV, and BESS
    profiles_hh_pv = _get_combined_profiles(profiles_hh, -profiles_pv)
    if profiles_bess is not None:
        profiles_hh_pv_bess = _get_combined_profiles(profiles_hh_pv, profiles_bess)
    else:
        profiles_hh_pv_bess = profiles_hh_pv
    profiles_hh_pv[profiles_hh_pv < 0] = 0
    profiles_hh_pv_bess[profiles_hh_pv_bess < 0] = 0
    # Determine profiles with EV and EV in combination with PV, and BESS
    # Todo: bess should be added as well
    if profiles_ev is not None:
        profiles_hh_ev = _get_combined_profiles(profiles_hh, profiles_ev)
    else:
        profiles_hh_ev = profiles_hh
    profiles_hh_ev_pv = _get_combined_profiles(profiles_hh_ev, -profiles_pv)
    if profiles_bess is not None:
        profiles_hh_ev_pv_bess = \
            _get_combined_profiles(profiles_hh_ev_pv, profiles_bess)
    else:
        profiles_hh_ev_pv_bess = profiles_hh_ev_pv
    profiles_hh_ev_pv[profiles_hh_ev_pv < 0] = 0
    profiles_hh_ev_pv_bess[profiles_hh_ev_pv_bess < 0] = 0
    return profiles_hh_pv, profiles_hh_pv_bess, profiles_hh_ev, profiles_hh_ev_pv, \
        profiles_hh_ev_pv_bess


def determine_cost_reduction_by_purchase_of_pv(
        profiles_hh, profiles_hh_pv, profiles_hh_pv_bess, profiles_hh_ev,
        profiles_hh_ev_pv, profiles_hh_ev_pv_bess):
    """
    Determine possible cost reduction by purchase of PV system for different network
    tariffs.

    :param profiles_hh:
    :param profiles_hh_pv:
    :param profiles_hh_pv_bess:
    :param profiles_hh_ev:
    :param profiles_hh_ev_pv:
    :param profiles_hh_ev_pv_bess:
    :return:
    """
    def _determine_reduction_potential(tariff_type):
        def _get_relative_reduction(profile_new, profile_base):
            ind_base = profile_base.apply(method)
            ind_new = profile_new.apply(method)
            idx = ind_new.reset_index()["index"].str.split(
                "-", expand=True)
            idx = idx.loc[:, 0:len(idx.columns) - 2].agg('-'.join, axis=1)
            return (ind_new / ind_base[idx].values).mean()

        def _get_monthly_peak(df):
            return df.groupby(df.index.month).max().sum()

        def _get_contracted_capacity(df):
            def _determine_constracted_capacity(peak):
                """
                Method to check which capacity tier is chosen for a certain peak value.

                :param peak: float
                    Consumption peak
                :return: float
                    Value for contracted capacity
                """
                capacity_tiers = [5, 10, 15, 20, 25]
                capacity_tiers.reverse()# Todo: change to actually used values
                contracted_capacity = 0
                for tier in capacity_tiers:
                    if peak <= tier:
                        contracted_capacity = tier
                    elif peak > tier:
                        break
                return contracted_capacity
            return _determine_constracted_capacity(df.max())
        if tariff_type == "VT":
            method = sum
        elif tariff_type == "MPT":
            method = _get_monthly_peak
        elif tariff_type == "YPT":
            method = max
        elif tariff_type == "CT":
            method = _get_contracted_capacity
        else:
            raise NotImplementedError
        consumer_group = "PV"
        reduction_potential.loc[consumer_group, tariff_type] = \
            _get_relative_reduction(
                profile_new=profiles_hh_pv,
                profile_base=profiles_hh
            )
        consumer_group = "PV_BESS"
        reduction_potential.loc[consumer_group, tariff_type] = \
            _get_relative_reduction(
                profile_new=profiles_hh_pv_bess,
                profile_base=profiles_hh
            )
        consumer_group = "EV_PV"
        reduction_potential.loc[consumer_group, tariff_type] = \
            _get_relative_reduction(
                profile_new=profiles_hh_ev_pv,
                profile_base=profiles_hh_ev
            )
        consumer_group = "EV_PV_BESS"
        reduction_potential.loc[consumer_group, tariff_type] = \
            _get_relative_reduction(
                profile_new=profiles_hh_ev_pv_bess,
                profile_base=profiles_hh_ev
            )

    # Set up dataframe
    tariffs = ["VT", "MPT", "YPT", "CT"]
    consumer_groups = ["PV", "PV_BESS", "EV_PV", "EV_PV_BESS"]
    reduction_potential = pd.DataFrame(index=consumer_groups, columns=tariffs)

    # Volumetric Tariff
    _determine_reduction_potential("VT")
    # Monthly Power Peak Tariff
    _determine_reduction_potential("MPT")
    # Monthly Yearly Peak Tariff
    _determine_reduction_potential("YPT")
    # Monthly Capacity Tariff
    _determine_reduction_potential("CT")

    return reduction_potential


if __name__ == "__main__":
    calculate_pv_cost_reduction = True
    calculate_cost_contribution = False
    # Cost reduction through purchase of PV system
    if calculate_pv_cost_reduction:
        data_dir = r"C:\Users\aheider\Downloads"
        # Todo: If you have the real data, the following block is not necessary
        hh_profiles = pd.read_excel(os.path.join(data_dir, "220530_PV_Calculations.xlsx"),
                                    sheet_name='grundverbrauch', index_col=0,
                                    parse_dates=True)[["C1", "C2", "C3", "C4", "C5"]]
        pv_profiles = pd.read_excel(os.path.join(data_dir, "220530_PV_Calculations.xlsx"),
                                    sheet_name='PV', index_col=0, parse_dates=True).loc[:,
                      ["PV_1", "PV_2", "PV_3", "PV_4"]].drop(index=["SUM", "MAX"])
        pv_profiles.index = pd.to_datetime(pv_profiles.index)
        ev_profiles = pd.read_excel(os.path.join(data_dir, "220530_PV_Calculations.xlsx"),
                                    sheet_name='emob', index_col=0, parse_dates=True).loc[:,
                      ["E_Mob_PHEV_1", "E_Mob_BEV_1", "E_Mob_PHEV_2", "E_Mob_BEV_2",
                       "E_Mob_PHEV_3"]].drop(index=["SUM", "MAX"])
        ev_profiles.index = pd.to_datetime(ev_profiles.index)
        hh_pv_profiles, hh_pv_bess_profiles, hh_ev_profiles, hh_ev_pv_profiles, \
            hh_ev_pv_bess_profiles = get_profiles_of_different_consumer_groups(
                hh_profiles, pv_profiles, profiles_ev=ev_profiles)
        # Todo: start from here, if data is available
        reduction_potential_pv = determine_cost_reduction_by_purchase_of_pv(
            hh_profiles, hh_pv_profiles, hh_pv_bess_profiles, hh_ev_profiles,
            hh_ev_pv_profiles, hh_ev_pv_bess_profiles
        )
        reduction_potential_pv.to_csv("pv_cost_reduction.csv")
    if calculate_cost_contribution:
        cost_contribution_ur, cost_contribution_cr = \
            determine_usage_and_capacity_related_cost_contributions()
        cost_contribution_ur.to_csv("cost_contribution_ur.csv")
