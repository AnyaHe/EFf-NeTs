import numpy as np
from numpy.linalg import eig
import pandas as pd

from indicators import add_names_criteria


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
        weighting_dict["Political Objectives"]
    ))
    weights['Stakeholder'] = [stakeholder]
    return weights.set_index("Stakeholder")


def priorities(pairwise_comparison_matrix):
    """
    Method to extract rated eigenvector for weighting

    :param pairwise_comparison_matrix: np.array
        NxN-matrix with pairwise comparison of N criteria. Comparative ratings are:
        1: Equally preferred
        2: Equally to moderately preferred
        3: Moderately preferred
        4: Moderately to strongly preferred
        5: Strongly preferred
        6: Strongly to very strongly preferred
        7: Very strongly preferred
        8: Very strongly to extremely preferred
        9: Extremely preferred
        Example matrix with criteria a and b where a is moderately preferred to b:
            a    b
        a [[1,   3],
        b [1/3,  1]]
    :return: np.array
        Relative weights of N criteria, in example above for [a, b]
        [0.75, 0.25]
    """
    # Eigenvector resulting in criteria's weights
    eig_vec = eig(pairwise_comparison_matrix)[1][:, 0]
    rated_eig_vec = eig_vec / eig_vec.sum()
    rated_eig_vec = np.real(rated_eig_vec)
    return rated_eig_vec


def extract_weights(pairwise_comparison_main,
                    pairwise_comparison_political_objectives):
    """
    Method to extract relative weights from comparison matrices.

    :param pairwise_comparison_main: np.array (3x3)
        Comparison matrix for main criteria:
        (i) efficient grid, (ii) fairness and customer acceptance,
        (iii) consistency with political objectives
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
    weights = np.ones([1, 4])
    # extract priorities for main- and sub-criteria
    priorities_main = priorities(pairwise_comparison_main)
    priorities_pol_objectives = priorities(pairwise_comparison_political_objectives)
    # combine weights of main and sub-criteria
    weights[0, 0] = priorities_main[0]
    weights[0, 1] = priorities_main[1]
    weights[0, 2] = priorities_pol_objectives[0] * priorities_main[2]
    weights[0, 3] = priorities_pol_objectives[1] * priorities_main[2]
    weights = pd.DataFrame(weights)
    return weights


