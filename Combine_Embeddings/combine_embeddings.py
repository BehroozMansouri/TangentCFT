from enum import Enum
import numpy as np


class Merge_Type(Enum):
    Sum = 1
    Concatenate = 2


def concatenate_list(lst_formula_maps):
    """
    This function takes in the list of formulas dictionary. Each list contains, a dictionary
    of formulas and their vector representation.
    :param lst_formula_maps:
    :return: dictionary of formulas of their vector representation, which is the concatenation of
    the input vectors.
    """
    result_map_result = {}
    map_zero = lst_formula_maps[0]
    for formula_id in map_zero:
        all_exist = True
        formula_vector = map_zero[formula_id]
        for lst_index in range(1, len(lst_formula_maps)):
            if formula_id not in lst_formula_maps[lst_index]:
                all_exist = False
                break
            else:
                formula_vector_temp = lst_formula_maps[lst_index][formula_id]
                formula_vector = np.concatenate([formula_vector, formula_vector_temp], axis=0)
        if all_exist:
            result_map_result[formula_id] = formula_vector
    return result_map_result


def sum_list(lst_formula_maps):
    """
    This function takes in the list of formulas dictionary. Each list contains, a dictionary
    of formulas and their vector representation.
    :param lst_formula_maps:
    :return: dictionary of formulas of their vector representation, which is the summation of
    the input vectors.
    """
    result_map_result = {}
    map_zero = lst_formula_maps[0]
    for formula_id in map_zero:
        all_exist = True
        formula_vector = map_zero[formula_id]
        for lst_index in range(1, len(lst_formula_maps)):
            if lst_formula_maps[lst_index][formula_id] is None:
                all_exist = False
                break
            else:
                formula_vector_temp = lst_formula_maps[lst_index][formula_id]
                formula_vector = formula_vector + formula_vector_temp
        if all_exist:
            result_map_result[formula_id] = formula_vector
    return result_map_result
