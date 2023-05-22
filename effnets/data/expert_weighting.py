import numpy as np


def expert_pairwise_comparison_dict():
    """
    Input data provided by experts representing the different stakeholder groups

    :return: dict
        Dictionary containing matrix of pairwise comparison of main criteria ("Main"),
        sub-criteria of efficient grid ("Efficient Grid") and other political objectives
        ("Political Objectives") for the different stakeholders ("DSO", "Authority",
        "Regulator", "Politics", "Third Party")
    """
    return {
        "Authority": {
            "Main": np.array([[1, 6, 5],
                              [1/6, 1, 2],
                              [1/5, 1/2, 1]]),
            "Efficient Grid":  np.array([[1, 3],
                                         [1/3, 1]]),
            "Political Objectives": np. array([[1, 1/4],
                                               [4, 1]])
        },
        "DSO": {
            "Main": np.array([[1, 7, 9],
                              [1/7, 1, 3],
                              [1/9, 1/3, 1]]),
            "Efficient Grid": np.array([[1, 1/5],
                                        [5, 1]]),
            "Political Objectives": np. array([[1, 1],
                                               [1, 1]])
        },
        "Politics": {
            "Main": np.array([[1, 1 / 5, 1 / 5],
                              [5, 1, 1],
                              [5, 1, 1]]),
            "Efficient Grid": np.array([[1, 5],
                                        [1 / 5, 1]]),
            "Political Objectives": np.array([[1, 3],
                                              [1 / 3, 1]])
        },
        "Regulator": {
            "Main": np.array([[1, 9, 7],
                              [1/9, 1, 2],
                              [1/7, 1/2, 1]]),
            "Efficient Grid": np.array([[1, 1/7],
                                        [7, 1]]),
            "Political Objectives": np.array([[1, 1],
                                              [1, 1]])
        },
        "Third Party": {
            "Main": np.array([[1, 5, 1],
                              [1/5, 1, 1/5],
                              [1, 5, 1]]),
            "Efficient Grid": np.array([[1, 5],
                                        [1/5, 1]]),
            "Political Objectives": np. array([[1, 1/3],
                                               [3, 1]])
        },
    }
