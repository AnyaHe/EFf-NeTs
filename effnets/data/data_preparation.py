# Methods to provide certain input data
import pandas as pd
import os
from itertools import product
import pathlib


def import_data():
    """
    Method to read input data and rename columns to expected names.

    :return: pandas.DataFrame
        columns contain ["Customer Group", "Group Share", "Cost Share", "Peak Share",
        "Energy Share", "Capacity Share", "Electricity Purchased", "Aggregated Peak",
        "Simultaneous Peak", "Contracted Capacity", "Losses", "Losses Share"]
    """
    # Import input data from simulated network
    data_dir = pathlib.Path(__file__).parent.resolve()
    data = pd.read_excel(os.path.join(data_dir, 'inputdata_new.xlsx'),
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
        "AggregiertePglz": "Aggregated Simultaneous Peak",
        "Peak_share_mean_total": "Simultaneous Peak",
        "AggregierteCap": "Contracted Capacity",
        "Total_Losses": "Losses",
        "relative_Losses": "Losses Share"
    }
    return data.rename(columns=rename_dict)


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
    # determine parameter for usage and capacity related costs
    param_ur = 'Simultaneous Peak'
    param_cr = 'Contracted Capacity'
    # get data of base scenario
    dt = import_data()
    base_dt = dt[(dt['Scenario'] == 1) & (dt['Alternative'] == 1)]
    peak_base = base_dt[param_ur].sum()
    capacity_base = base_dt[param_cr].sum()
    # get cost contribution of peaks and capacity
    cost_contribution_ur = pd.DataFrame()
    cost_contribution_cr = pd.DataFrame()
    for scenario in dt["Scenario"].unique():
        for alternative in dt["Alternative"].unique():
            # adapt to new alternative and scenario, Eq. (33)
            peak = dt[(dt['Scenario'] == scenario) &
                      (dt['Alternative'] == alternative)][param_ur].sum()
            ur_tmp = ur_base * peak / peak_base
            # adapt to new alternative and scenario, Eq. (34)
            capacity = \
                dt[(dt['Scenario'] == scenario) &
                   (dt['Alternative'] == alternative)][param_cr].sum()
            cr_tmp = cr_base * capacity / capacity_base
            # normalise so sum is 1, Eq. (35)
            cost_contribution_ur.loc[scenario, alternative] = ur_tmp/(ur_tmp+cr_tmp)
            cost_contribution_cr.loc[scenario, alternative] = cr_tmp / (ur_tmp + cr_tmp)
    return cost_contribution_ur, cost_contribution_cr


def get_profiles_of_different_consumer_groups(
        profiles_hh_cg4, profiles_pv_cg4, profiles_hh_cg5, profiles_pv_cg5,
        profiles_bess_cg4=None, profiles_ev_cg5=None, profiles_bess_cg5=None):
    """
    Method to generate combined profiles with representative time series of households
    (hh), PV, BESS and EVs.

    :param profiles_hh_cg4:
    :param profiles_pv_cg4:
    :param profiles_hh_cg5:
    :param profiles_pv_cg5:
    :param profiles_bess_cg4:
    :param profiles_ev_cg5:
    :param profiles_bess_cg5:
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
        combined_profiles = profiles_1 + profiles_2.values
        return combined_profiles

    # Todo: might not be necessary, if you just enter the profiles
    # Determine profiles HH with PV, and BESS for CG4
    profiles_hh_pv_cg4 = _get_combined_profiles(profiles_hh_cg4, -profiles_pv_cg4)
    if profiles_bess_cg4 is not None:
        profiles_hh_pv_bess_cg4 = _get_combined_profiles(
            profiles_hh_cg4, -profiles_pv_cg4+profiles_bess_cg4.values)
    else:
        profiles_hh_pv_bess_cg4 = profiles_hh_pv_cg4
    profiles_hh_pv_cg4[profiles_hh_pv_cg4 < 0] = 0
    profiles_hh_pv_bess_cg4[profiles_hh_pv_bess_cg4 < 0] = 0
    # Determine profiles with EV and EV in combination with PV, and BESS
    # Todo: bess should be added as well
    if profiles_ev_cg5 is not None:
        profiles_hh_ev_cg5 = _get_combined_profiles(profiles_hh_cg5, profiles_ev_cg5)
    else:
        profiles_hh_ev_cg5 = profiles_hh_cg5
    profiles_hh_ev_pv_cg5 = _get_combined_profiles(profiles_hh_ev_cg5, -profiles_pv_cg5)
    if profiles_bess_cg5 is not None:
        profiles_hh_ev_pv_bess_cg5 = \
            _get_combined_profiles(profiles_hh_ev_cg5,
                                   -profiles_pv_cg5+profiles_bess_cg5.values)
    else:
        profiles_hh_ev_pv_bess_cg5 = profiles_hh_ev_pv_cg5
    profiles_hh_ev_pv_cg5[profiles_hh_ev_pv_cg5 < 0] = 0
    profiles_hh_ev_pv_bess_cg5[profiles_hh_ev_pv_bess_cg5 < 0] = 0
    return profiles_hh_pv_cg4, profiles_hh_pv_bess_cg4, \
           profiles_hh_ev_cg5, profiles_hh_ev_pv_cg5, profiles_hh_ev_pv_bess_cg5


def determine_cost_reduction_by_purchase_of_pv(
        profiles_hh_cg4, profiles_hh_pv_cg4, profiles_hh_pv_bess_cg4,
        profiles_hh_ev_cg5, profiles_hh_ev_pv_cg5, profiles_hh_ev_pv_bess_cg5):
    """
    Determine possible cost reduction by purchase of PV system for different network
    tariffs

    :param profiles_hh_cg4:
    :param profiles_hh_pv_cg4:
    :param profiles_hh_pv_bess_cg4:
    :param profiles_hh_ev_cg5:
    :param profiles_hh_ev_pv_cg5:
    :param profiles_hh_ev_pv_bess_cg5:
    :return:
    """
    def _determine_reduction_potential(tariff_type):
        def _get_relative_reduction(profile_new, profile_base):
            ind_base = profile_base.apply(method)
            ind_new = profile_new.apply(method)
            return (ind_new / ind_base.values).mean()

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
                capacity_tiers = [3, 5, 7, 6*1.44, 10*1.44, 13*1.44, 16*1.44, 20*1.44,
                                  25*1.44, 32*1.44, 35*1.44, 40*1.44, 50*1.44, 63*1.44]
                capacity_tiers.reverse()
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
                profile_new=profiles_hh_pv_cg4,
                profile_base=profiles_hh_cg4
            )
        consumer_group = "PV_BESS"
        reduction_potential.loc[consumer_group, tariff_type] = \
            _get_relative_reduction(
                profile_new=profiles_hh_pv_bess_cg4,
                profile_base=profiles_hh_cg4
            )
        consumer_group = "EV_PV"
        reduction_potential.loc[consumer_group, tariff_type] = \
            _get_relative_reduction(
                profile_new=profiles_hh_ev_pv_cg5,
                profile_base=profiles_hh_ev_cg5
            )
        consumer_group = "EV_PV_BESS"
        reduction_potential.loc[consumer_group, tariff_type] = \
            _get_relative_reduction(
                profile_new=profiles_hh_ev_pv_bess_cg5,
                profile_base=profiles_hh_ev_cg5
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


def determine_proxy_of_cost_reduction_der(simplified=False):
    """
    Determine proxy for reduction potential, reduction of cost driving factors compared
    to group shares, compared are PV-owners (CG2) and PV-BESS-owners (CG4) to inflexible
    consumers (CG1) and PV-EV-BESS (CG5) to EV-owners (CG3).

    :return:
    """
    # determine parameter for cost driving factors
    if not simplified:
        tariff_dict = {
            1: {"name": "VT", "proxy": "Electricity Purchased"},
            2: {"name": "MPT", "proxy": "Monthly Peak"},
            3: {"name": "YPT", "proxy": "Aggregated Peak"},
            4: {"name": "CT", "proxy": "Contracted Capacity"},
        }
    else:
        tariff_dict = {
            1: {"name": "VT", "proxy": "Cost Share"},
            2: {"name": "MPT", "proxy": "Cost Share"},
            3: {"name": "YPT", "proxy": "Cost Share"},
            4: {"name": "CT", "proxy": "Cost Share"},
        }
    # get data of base scenario
    dt = import_data()
    # Set up dataframe
    tariffs = ["VT", "MPT", "YPT", "CT"]
    consumer_groups = ["PV", "PV_BESS", "EV_PV", "EV_PV_BESS"]
    reduction_potential = pd.DataFrame(index=consumer_groups, columns=tariffs)
    for t_index, t_inf in tariff_dict.items():
        dt_tmp = dt.loc[(dt.Alternative == t_index) & (dt.Scenario.isin([1, 2, 3, 4]))]
        dt_tmp["Relative Cost Driver"] = dt_tmp[t_inf["proxy"]]/dt_tmp["Group Share"]
        reduction_pv = \
            dt_tmp.loc[dt_tmp["Customer Group"] == 2, "Relative Cost Driver"].divide(
                dt_tmp.loc[dt_tmp["Customer Group"] == 1, "Relative Cost Driver"].values
            )
        reduction_pv_bess =  \
            dt_tmp.loc[dt_tmp["Customer Group"] == 4, "Relative Cost Driver"].divide(
                dt_tmp.loc[dt_tmp["Customer Group"] == 1, "Relative Cost Driver"].values
            )
        reduction_ev_pv_bess = \
            dt_tmp.loc[dt_tmp["Customer Group"] == 5, "Relative Cost Driver"].divide(
                dt_tmp.loc[dt_tmp["Customer Group"] == 3, "Relative Cost Driver"].values
            )
        reduction_potential.loc["PV", t_inf["name"]] = reduction_pv.mean()
        reduction_potential.loc["PV_BESS", t_inf["name"]] = reduction_pv_bess.mean()
        reduction_potential.loc["EV_PV", t_inf["name"]] = reduction_ev_pv_bess.mean()
        reduction_potential.loc["EV_PV_BESS", t_inf["name"]] = reduction_ev_pv_bess.mean()
    return reduction_potential


if __name__ == "__main__":
    calculate_pv_cost_reduction_proxy = False
    calculate_pv_cost_reduction = False
    calculate_cost_contribution = True
    # Cost reduction through purchase of PV system
    if calculate_pv_cost_reduction_proxy:
        reduction_potential_pv = determine_proxy_of_cost_reduction_der(simplified=False)
        reduction_potential_pv.to_csv("pv_cost_reduction.csv")
    if calculate_pv_cost_reduction:
        data_dir = r"C:\Users\aheider\Downloads"
        # Todo: use data of CG5 here
        hh_profiles_cg5 = pd.read_excel(os.path.join(data_dir, "220530_PV_Calculations.xlsx"),
                                    sheet_name='grundverbrauch', index_col=0,
                                    parse_dates=True)[["C1", "C2", "C3", "C4"]]
        pv_profiles_cg5 = pd.read_excel(os.path.join(data_dir, "220530_PV_Calculations.xlsx"),
                                    sheet_name='PV', index_col=0, parse_dates=True).loc[:,
                      ["PV_1", "PV_2", "PV_3", "PV_4"]].drop(index=["SUM", "MAX"])
        pv_profiles_cg5.index = pd.to_datetime(pv_profiles_cg5.index)
        ev_profiles_cg5 = pd.read_excel(os.path.join(data_dir, "220530_PV_Calculations.xlsx"),
                                    sheet_name='emob', index_col=0, parse_dates=True).loc[:,
                      ["E_Mob_PHEV_1", "E_Mob_BEV_1", "E_Mob_PHEV_2", "E_Mob_BEV_2"]].drop(index=["SUM", "MAX"])
        ev_profiles_cg5.index = pd.to_datetime(ev_profiles_cg5.index)
        bess_profiles_cg5 = pd.DataFrame(data=0, index=hh_profiles_cg5.index,
                                         columns=["B_1", "B_2", "B_3", "B_4"])
        # Todo: use data of CG4 here
        hh_profiles_cg4 = \
        pd.read_excel(os.path.join(data_dir, "220530_PV_Calculations.xlsx"),
                      sheet_name='grundverbrauch', index_col=0,
                      parse_dates=True)[["C1", "C2", "C3", "C4"]]
        pv_profiles_cg4 = pd.read_excel(
            os.path.join(data_dir, "220530_PV_Calculations.xlsx"),
            sheet_name='PV', index_col=0, parse_dates=True).loc[:,
                      ["PV_1", "PV_2", "PV_3", "PV_4"]].drop(index=["SUM", "MAX"])
        pv_profiles_cg4.index = pd.to_datetime(pv_profiles_cg4.index)
        bess_profiles_cg4 = pd.DataFrame(data=0, index=hh_profiles_cg4.index,
                                         columns=["B_1", "B_2", "B_3", "B_4"])
        # combine profiles
        hh_pv_profiles_cg4, hh_pv_bess_profiles_cg4, \
        hh_ev_profiles_cg5, hh_ev_pv_profiles_cg5, hh_ev_pv_bess_profiles_cg5 = \
            get_profiles_of_different_consumer_groups(
                profiles_hh_cg4=hh_profiles_cg4,
                profiles_pv_cg4=pv_profiles_cg4,
                profiles_hh_cg5=hh_profiles_cg5,
                profiles_pv_cg5=pv_profiles_cg5,
                profiles_bess_cg4=bess_profiles_cg4,
                profiles_ev_cg5=ev_profiles_cg5,
                profiles_bess_cg5=bess_profiles_cg5
        )
        # Todo: start from here, if data is available
        reduction_potential_pv = determine_cost_reduction_by_purchase_of_pv(
            profiles_hh_cg4=hh_profiles_cg4,
            profiles_hh_pv_cg4=hh_pv_profiles_cg4,
            profiles_hh_pv_bess_cg4=hh_pv_bess_profiles_cg4,
            profiles_hh_ev_cg5=hh_ev_profiles_cg5,
            profiles_hh_ev_pv_cg5=hh_ev_pv_profiles_cg5,
            profiles_hh_ev_pv_bess_cg5=hh_ev_pv_bess_profiles_cg5
        )
        reduction_potential_pv.to_csv("pv_cost_reduction.csv")
    if calculate_cost_contribution:
        cost_contribution_ur, cost_contribution_cr = \
            determine_usage_and_capacity_related_cost_contributions()
        cost_contribution_ur.to_csv("cost_contribution_ur.csv")
