from sys import argv
import torch
from torch.autograd import Variable
import numpy
import os
import numpy as np
os.environ['CUDA_VISIBLE_DEVICES']='0'
use_cuda = torch.cuda.is_available()
import torch.nn.functional as F
import datetime
from scipy import spatial

def read_query_vectors(directory_path, dimension):
    result = {}
    for i in range(1, 69):
        filename = directory_path + "/" + str(i) + ".txt"
        file = open(filename)
        formula_vector = numpy.loadtxt(file).reshape(1, dimension)
        temp = Variable(torch.tensor(formula_vector).double()).cuda()
        result[i] = temp
    return result


def ReadAllFileVectors(files_directory, dimension):
    result = {}
    numpy_lst = []
    idx = 0

    for i in range(1, 17):
        for filename in os.listdir(files_directory + "/" + str(i)):
            file = open(files_directory + "/" + str(i) + "/" + filename)
            parts = filename.split(".")
            temp_name = parts[0]
            for k in range(1, len(parts)-1):
                temp_name = temp_name + "." + parts[k]
            formula_vector = np.array(numpy.loadtxt(file)).reshape(1, dimension)
            numpy_lst.append(formula_vector)
            result[idx] = temp_name
            idx += 1

    temp = np.concatenate(numpy_lst, axis=0)
    tensor_values = Variable(torch.tensor(temp).double()).cuda()
    return result, tensor_values


def read_specific_files(files_directory, dimension, lst_file):
    result = {}
    numpy_lst = []
    idx = 0

    for i in range(1, 17):
        for filename in os.listdir(files_directory + "/" + str(i)):
            file = open(files_directory + "/" + str(i) + "/" + filename)
            parts = filename.split(".")
            temp_name = parts[0]
            for k in range(1, len(parts)-1):
                temp_name = temp_name + "." + parts[k]
            if temp_name not in lst_file:
                continue
            formula_vector = np.array(numpy.loadtxt(file)).reshape(1, dimension)
            numpy_lst.append(formula_vector)
            result[idx] = temp_name
            idx += 1

    temp = np.concatenate(numpy_lst, axis=0)
    tensor_values = Variable(torch.tensor(temp).double()).cuda()
    return result, tensor_values


def result_generator(i, dimension):
    doc_id_map, doc_tensors = ReadAllFileVectors("/home/bm3302/FastText/Run_Result_"+str(i), dimension)
    query_vector_map = read_query_vectors("/home/bm3302/FastText/Run_Result_" + str(i) + "/Queries", dimension)
    sum = .0
    counter = 0
    f = open('/home/bm3302/FastText/ResultFiles/Res_Top_'+str(i)+'.txt', 'w')
    for queryId in query_vector_map:
        query_vec = query_vector_map[queryId]
        t1 = datetime.datetime.now()
        dist = F.cosine_similarity(doc_tensors, query_vec)
        index_sorted = torch.sort(dist, descending=True)[1]
        top_1000 = index_sorted[:1000]
        t2 = datetime.datetime.now()
        top_1000 = top_1000.data.cpu().numpy()
        sum += (t2 - t1).total_seconds() * 1000.0
        counter += 1
        cos_values = torch.sort(dist, descending=True)[0][:1000].data.cpu().numpy()
        count = 1
        query = "NTCIR12-MathWiki-" + str(queryId)
        line = query + " xxx "
        for x in top_1000:
            doc_id = doc_id_map[x]
            score = cos_values[count-1]
            temp = line + doc_id + " " + str(count) + " " + str(score) + " Run_" + str(i)
            f.write(temp + "\n")
            count += 1
    f.close()
    print(sum/counter)


def result_generator_for_unified_step_one(i, dimension):
    doc_id_map, doc_tensors = ReadAllFileVectors("/home/bm3302/FastText/Run_Result_"+str(i), dimension)
    query_vector_map = read_query_vectors("/home/bm3302/FastText/Run_Result_" + str(i) + "/Queries", dimension)
    sum = .0
    counter = 0
    f = open('/home/bm3302/FastText/ResultFiles/Res_Top_'+str(i)+'.txt', 'w')
    for queryId in query_vector_map:
        query_vec = query_vector_map[queryId]
        t1 = datetime.datetime.now()
        dist = F.cosine_similarity(doc_tensors, query_vec)
        index_sorted = torch.sort(dist, descending=True)[1]
        top_1000 = index_sorted[:5000]
        t2 = datetime.datetime.now()
        top_1000 = top_1000.data.cpu().numpy()
        sum += (t2 - t1).total_seconds() * 1000.0
        counter += 1
        cos_values = torch.sort(dist, descending=True)[0][:5000].data.cpu().numpy()
        count = 1
        query = "NTCIR12-MathWiki-" + str(queryId)
        line = query + " xxx "
        temp_counter = 0
        lst_score = -1
        for x in top_1000:
            doc_id = doc_id_map[x]
            score = cos_values[count-1]

            if(temp_counter>2000 and score!=lst_score):
                break

            temp = line + doc_id + " " + str(count) + " " + str(score) + " Run_" + str(i)
            f.write(temp + "\n")

            temp_counter += 1
            lst_score = score


            count+=1
    f.close()
    print(sum/counter)


def main(argv):
    value1 = int(argv[1])
    value2 = int(argv[2])
    dimension = int(argv[3])
    for i in range(value1, value2):
        result_generator(i, dimension)
        print("config File finished"+str(i))


if __name__ == '__main__':
    main(argv)