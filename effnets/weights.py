import numpy as np
from numpy.linalg import eig
import pandas as pd


def get_relative_weights_stakeholder(weighting_dict, stakeholder):
    """
    Method to extract relative weights with pairwise comparison of stakehodler
    representative.


    :param weighting_dict: dict

    :param stakeholder:
    :return: pd.DataFrame
        column names: see addnames()
        index: input stakeholder
    """
    weights = add_names_criteria(extract_weights(
        weighting_dict["Main"],
        weighting_dict["Efficient Grid"],
        weighting_dict["Political Objectives"]
    ))
    weights['Stakeholder'] = [stakeholder]
    return weights.set_index("Stakeholder")


def priorities(pairwise_comparison_matrix):
    """
    Method to extract rated eigenvector for weighting

    :param pairwise_comparison_matrix: np.array
        NxN-matrix with pairwise comparison of N criteria. Todo: explain further
    :return:
    """
    # Eigenvector resulting in criteria's weights
    eig_vec = eig(pairwise_comparison_matrix)[1][:, 0]
    rated_eig_vec = eig_vec / eig_vec.sum()
    rated_eig_vec = np.real(rated_eig_vec)
    return rated_eig_vec


def extract_weights(pairwise_comparison_main, pairwise_comparison_efficient_grid,
                    pairwise_comparison_political_objectives):
    """
    Method to extract relative weights from comparison matrices.

    :param pairwise_comparison_main: np.array (3x3)
        Comparison matrix for main criteria:
        (i) efficient grid, (ii) fairness and customer acceptance,
        (iii) consistency with political objectives
    :param pairwise_comparison_efficient_grid: np.array (2x2)
        Comparison matrix for sub-criteria with respect to an efficient grid:
        (i) reflection of usage-related costs, (ii) reflection of capacity-related costs
    :param pairwise_comparison_political_objectives: np.array (2x2)
        Comparison matrix for sub-criteria with respect to consistency with political
        objectives
        (i) expansion of DER, (ii) efficient electricity usage
    :return: pd.DataFrame()
        Relative weights of all criteria and sub-criteria, namely:
        0: reflection of usage-related costs
        1: reflection of capacity-related costs
        2: fairness and customer acceptance
        3: expansion of DER
        4: efficient electricity usage
    """
    # initialise weights
    weights = np.ones([1, 5])
    # extract priorities for main- and sub-criteria
    priorities_main = priorities(pairwise_comparison_main)
    priorities_eff_grid = priorities(pairwise_comparison_efficient_grid)
    priorities_pol_objectives = priorities(pairwise_comparison_political_objectives)
    # combine weights of main and sub-criteria
    weights[0, 0] = priorities_eff_grid[0] * priorities_main[0]
    weights[0, 1] = priorities_eff_grid[1] * priorities_main[0]
    weights[0, 2] = priorities_main[1]
    weights[0, 3] = priorities_pol_objectives[0] * priorities_main[2]
    weights[0, 4] = priorities_pol_objectives[1] * priorities_main[2]
    weights = pd.DataFrame(weights)
    return weights


def add_names_criteria(df):
    """
    Help function to add names of criteria to existing dataframe with five columns

    :param df: pd.DataFrame
        Containing data on evaluated criteria, columns have to correspond to criteria
    :return:
    """
    df.columns = ['Reflection of Usage-Related Costs',
                  'Reflection of Capacity-Related Costs',
                  'Fairness and Customer Acceptance',
                  'Expansion of DER', 'Efficient Electricity Usage']
    return df

