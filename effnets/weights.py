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
    weights = addnames(extract_weights(
        weighting_dict["Main"],
        weighting_dict["Efficient Grid"],
        weighting_dict["Political Objectives"]
    ))
    weights['Stakeholder'] = [stakeholder]
    return weights.set_index("Stakeholder")


def priorities(W):
    """
    Method to extract rated eigenvector for weighting

    :param W: np.array
        NxN-matrix with relative importances of N criteria. Todo: explain further
    :return:
    """
    # Eigenvector resulting in criteria's weights
    eig_vec = eig(W)[1][:, 0]
    p = eig_vec / eig_vec.sum()
    p = np.real(p)
    return p


def extract_weights(W, W_1, W_3):
    """
    Method to extract relative weights from comparison matrices.

    :param W: np.array (3x3)
        Comparison matrix for main criteria:
        (i) efficient grid, (ii) fairness and customer acceptance,
        (iii) consistency with political objectives
    :param W_1: np.array (2x2)
        Comparison matrix for sub-criteria with respect to an efficient grid:
        (i) reflection of usage-related costs, (ii) reflection of capacity-related costs
    :param W_3: np.array (2x2)
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
    # Combining weights of main and sub-criteria
    P = np.ones([1, 5])
    P[0, 0] = priorities(W_1)[0]*priorities(W)[0]
    P[0, 1] = priorities(W_1)[1]*priorities(W)[0]
    P[0, 2] = priorities(W)[1]
    P[0, 3] = priorities(W_3)[0]*priorities(W)[2]
    P[0, 4] = priorities(W_3)[1]*priorities(W)[2]
    W = pd.DataFrame(P)

    return W


def addnames(NA):
    NA.columns = ['Reflection of Usage-Related Costs',
                  'Reflection of Capacity-Related Costs',
                  'Fairness and Customer Acceptance',
                  'Expansion of DER', 'Efficient Electricity Usage']

    return NA

