"Here the goal is to study all the possible cases"
import itertools

import os
from sys import argv
import numpy as np


def save_result(result, map_result, lst):
    os.makedirs(result)
    for i in range(1, 17):
        os.makedirs(result + "/" + str(i))
    os.makedirs(result + "/" + "Queries")
    for item in map_result:
        address = item
        vector_index = map_result[item]
        vector_value = lst[vector_index]
        np.savetxt(address, vector_value, newline=" ")

def combine_files(lst_files, result_file_path, current_dimension, sum=True):
    map_result = {}
    lst = []
    counter = 0
    for directories in os.listdir(lst_files[0]):
        for filename in os.listdir(lst_files[0] + "/" + directories):

            all_exist = True
            for file_index in range(0, len(lst_files)):
                if not os.path.isfile(lst_files[file_index] + "/" + directories + "/" + filename):
                    all_exist = False
                    break
            if not all_exist:
                continue
            all_arrays = None
            for file_index in range(0, len(lst_files)):
                file = open(lst_files[file_index] + "/" + directories + "/" + filename)
                current_array = np.array(np.loadtxt(file)).reshape(1, current_dimension)
                if all_arrays is None:
                    all_arrays = current_array
                else:
                    if sum:
                        all_arrays += current_array
                    else:
                        all_arrays = np.concatenate((all_arrays, current_array), axis=None)

            lst.append(all_arrays)
            parts = filename.split(".")
            temp_name = parts[0]
            for k in range(1, len(parts) - 1):
                temp_name = temp_name + "." + parts[k]
            map_result[result_file_path + "/" + directories + "/" + temp_name + ".txt"] = counter
            counter += 1
    return map_result, lst


def main():
    lst = [702,703,704,732,720,738,707,715]
    #lst.append(715)
    counter = 7000
    file_com = open("/home/bm3302/FastText/combined_res5.txt", "w")
    for r in range(2, len(lst)):
        #lst.append(715)
        temp = set(itertools.combinations(lst, r))
        files_dimensions = 300

        is_sum = True

        for setitem in temp:
            print(counter)
            if counter<=7038:
                counter+=1
                continue
            result_file_path = "/home/bm3302/FastText/Run_Result_" + str(counter)
            file_com.write(str(counter) + ",")
            counter += 1
            lst_file = []
            for item in setitem:
                file_com.write(str(item)+",")
                lst_file.append("/home/bm3302/FastText/Run_Result_" + str(item))
            file_com.write("\n")
            map_result, lst = combine_files(lst_file, result_file_path, files_dimensions, is_sum)
            save_result(result_file_path, map_result, lst)
    file_com.close()
if __name__ == '__main__':
    main()