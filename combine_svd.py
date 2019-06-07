import os
import numpy as np
import os.path
from sklearn.decomposition import TruncatedSVD
from sklearn.decomposition import PCA
from sklearn.decomposition import FastICA
from sklearn.manifold import TSNE


def create_destination(result):
    os.makedirs(result)
    for i in range(1, 17):
        os.makedirs(result + "/" + str(i))
    os.makedirs(result + "/" + "Queries")


def combine_files(file1, file2, result, dimension,component):

    map_result = {}
    lst = []
    counter = 0
    for directories in os.listdir(file1):
        for filename in os.listdir(file1 + "/" + directories):
            file11 = open(file1 + "/" + directories + "/" + filename)

            if os.path.isfile(file2 + "/" + directories + "/" + filename) == False:
                continue

            file22 = open(file2 + "/" + directories + "/" + filename)
            parts = filename.split(".")
            temp_name = parts[0]
            for k in range(1, len(parts)-1):
                temp_name = temp_name + "." + parts[k]
            formula_vector_1 = np.array(np.loadtxt(file11)).reshape(1, dimension)
            formula_vector_2 = np.array(np.loadtxt(file22)).reshape(1, dimension)
            temp = np.concatenate((formula_vector_1, formula_vector_2), axis=None)
            lst.append(temp)
            map_result[result+"/"+directories+"/"+temp_name+".txt"] = counter
            counter += 1
    create_destination(result)
    lst = apply_TSNE(lst, component_size=component)
    for item in map_result:
        address = item
        vector_index = map_result[item]
        vector_value = lst[vector_index]
        np.savetxt(address, vector_value, newline=" ")


def apply_svd(matrix, component_size):
    svd = TruncatedSVD(n_components=component_size, n_iter=10)
    svd.fit(matrix)
    result = svd.transform(matrix)
    return result


def apply_pca(matrix, component_size):
    pca = PCA(n_components=component_size)
    result = pca.fit_transform(matrix)
    return result


def apply_ica(matrix, component_size):
    ica = FastICA(n_components=component_size)
    result = ica.fit_transform(matrix)
    return result


def apply_TSNE(matrix, component_size):
    result = TSNE(n_components=component_size).fit_transform(matrix)
    return result


def test():
    combine_files("/home/bm3302/FastText/Run_Result_34", "/home/bm3302/FastText/Run_Result_314", "/home/bm3302/FastText/Run_Result_tsne", 300, 256)


def main():
    test()


if __name__ == '__main__':
    main()