import os
import numpy as np
import os.path
from sklearn.decomposition import TruncatedSVD
from sklearn.decomposition import PCA
from sklearn.decomposition import FastICA
from sklearn.manifold import TSNE
from sys import argv


def create_destination(result):
    os.makedirs(result)
    for i in range(1, 17):
        os.makedirs(result + "/" + str(i))
    os.makedirs(result + "/" + "Queries")


def merge_files(result_file_path, current_dimension, lst_files):
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

            allArrays = None#np.array([])
            for file_index in range(0, len(lst_files)):
                file = open(lst_files[file_index] + "/" + directories + "/" + filename)
                formula_vector = np.array(np.loadtxt(file))#.reshape(1, current_dimension)
                if allArrays is None:
                    allArrays = formula_vector
                else:
                    allArrays += formula_vector

                #allArrays = np.concatenate([allArrays, formula_vector], axis=None)

            lst.append(allArrays)
            parts = filename.split(".")
            temp_name = parts[0]
            for k in range(1, len(parts) - 1):
                temp_name = temp_name + "." + parts[k]
            map_result[result_file_path + "/" + directories + "/" + temp_name + ".txt"] = counter
            counter += 1
    return map_result, lst


def combine_with_reduction(component, lst, map_result, reduction, result):
    create_destination(result)
    #reduction = "pca"
    if reduction is not None:
        if reduction == "ica":
            lst = apply_ica(lst, component_size=component)
        elif reduction == "pca":
            lst = apply_pca(lst, component_size=component)
        elif reduction == "svd":
            lst = apply_svd(lst, component_size=component)
        elif reduction == "tsne":
            lst = apply_TSNE(lst, component_size=component)
    for item in map_result:
        address = item
        vector_index = map_result[item]
        vector_value = lst[vector_index]
        np.savetxt(address, vector_value, newline=" ")


def combine_files(lst_files, result, dimension, component, reduction=None):
    map_result, lst = merge_files(result, dimension, lst_files)
    combine_with_reduction(component, lst, map_result, reduction, result)


def apply_svd(matrix, component_size):
    print("Applying SVD")
    svd = TruncatedSVD(n_components=component_size, n_iter=10)
    svd.fit(matrix)
    result = svd.transform(matrix)
    return result


def apply_pca(matrix, component_size):
    print("Applying PCA")
    pca = PCA(n_components='mle', svd_solver='full')
    result = pca.fit(matrix)
    pca.transform(matrix)
    return result


def apply_ica(matrix, component_size):
    print("Applying ICA")
    ica = FastICA(n_components=component_size)
    result = ica.fit_transform(matrix)
    return result


def apply_TSNE(matrix, component_size):
    print("Applying TSNE")
    result = TSNE(n_components=component_size).fit_transform(matrix)
    return result


def main():#argv):
    files_dimensions = 300#int(argv[1])
    new_dimension = 300#int(argv[2])
    result_file_path = "/home/bm3302/FastText/Run_Result_" + "9015"#argv[3]
    #lst_file = ["/home/bm3302/FastText/Run_Result_" + argv[4], "/home/bm3302/FastText/Run_Result_" + argv[5]]
    lst_file = ["/home/bm3302/FastText/Run_Result_503","/home/bm3302/FastText/Run_Result_422",
               "/home/bm3302/FastText/Run_Result_2013", "/home/bm3302/FastText/Run_Result_436","/home/bm3302/FastText/Run_Result_2063"]
    # if len(argv) == 7:
    #     print("Three files")
    #     lst_file.append("/home/bm3302/FastText/Run_Result_" + argv[6])
    combine_files(lst_file, result_file_path, files_dimensions, new_dimension)


if __name__ == '__main__':
    main()#argv)