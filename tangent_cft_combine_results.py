import argparse
import numpy as np
from torch.autograd import Variable
import torch
import torch.nn.functional as F
from Embedding_Preprocessing.encoder_tuple_level import TupleTokenizationMode
from tangent_cft_back_end import TangentCFTBackEnd
from tangent_cft_module import TangentCFTModule


def get_vectors(dataset_file_path, queries_directory_path, is_wiki, config_id, read_slt, encoder_file_path,
                model_file_path, tokenize_number=False, ignore_full_relative_path=True, tokenize_all=False,
                tokenization=3):
    embedding_type = TupleTokenizationMode(tokenization)
    map_file_path = "Embedding_Preprocessing/" + str(encoder_file_path)
    config_file_path = "Configuration/config/config_" + str(config_id)
    system = TangentCFTBackEnd(config_file=config_file_path, path_data_set=dataset_file_path, is_wiki=is_wiki,
                               read_slt=read_slt, queries_directory_path=queries_directory_path)
    dictionary_formula_tuples_collection = system.load_model(
        map_file_path=map_file_path,
        model_file_path=model_file_path,
        embedding_type=embedding_type, ignore_full_relative_path=ignore_full_relative_path,
        tokenize_all=tokenize_all,
        tokenize_number=tokenize_number
    )
    index_formula_id, query_vectors = system.get_collection_query_vectors(dictionary_formula_tuples_collection,
                                                                          embedding_type, ignore_full_relative_path,
                                                                          tokenize_all, tokenize_number)
    return index_formula_id, query_vectors


def sum_collection(tensor_values_slt, tensor_values_opt, tensor_values_slt_type):
    numpy_lst = []
    index_formula_id = {}
    idx = 0
    for formula_id in tensor_values_slt:
        temp = tensor_values_slt[formula_id]
        if formula_id in tensor_values_opt:
            temp = np.add(temp, tensor_values_opt[formula_id])
        if formula_id in tensor_values_slt_type:
            temp = np.add(temp, tensor_values_slt_type[formula_id])
        numpy_lst.append(temp)
        index_formula_id[idx] = formula_id
        idx += 1
    temp = np.concatenate(numpy_lst, axis=0)
    tensor_values = Variable(torch.tensor(temp).double()).cuda()
    return tensor_values, index_formula_id


def sum_queries(query_vectors_slt, query_vectors_opt, query_vectors_slt_type):
    result_map_result = {}
    for query_id in query_vectors_slt:
        formula_vector = query_vectors_slt[query_id]
        if query_id in query_vectors_opt:
            formula_vector = formula_vector + query_vectors_opt[query_id]
        if query_id in query_vectors_slt_type:
            formula_vector = formula_vector + query_vectors_slt_type[query_id]
        result_map_result[query_id] = formula_vector
    return result_map_result


def retrieval(collection_vectors, index_formula_id, query_vectors):
    retrieval_result = {}
    for query in query_vectors:
        query_vec = query_vectors[query]
        retrieval_result[query] = TangentCFTModule.formula_retrieval(collection_vectors, index_formula_id, query_vec)
    return retrieval_result


def main():

    dataset_file_path = "/NTCIR12_MathIR_WikiCorpus_v2.1.0/MathTagArticles"
    queries_directory_path = "/TestQueries"
    is_wiki = True

    index_formula_id_slt, query_vectors_slt = get_vectors(dataset_file_path, queries_directory_path,
                                                          is_wiki, config_id=1, read_slt=True,
                                                          encoder_file_path="slt_encoder.csv",
                                                          model_file_path="slt_model",
                                                          tokenize_number=True)
    index_formula_id_opt, query_vectors_opt = get_vectors(dataset_file_path, queries_directory_path,
                                                          is_wiki, config_id=2, read_slt=False,
                                                          encoder_file_path="opt_encoder.csv",
                                                          model_file_path="opt_model")
    index_formula_id_slt_type, query_vectors_slt_type = get_vectors(dataset_file_path,
                                                                    queries_directory_path,
                                                                    is_wiki, config_id=3,
                                                                    read_slt=True,
                                                                    encoder_file_path="slt_type_encoder.csv",
                                                                    model_file_path="slt_type_model",
                                                                    tokenization=2)

    tensor_values, index_formula_id = sum_collection(index_formula_id_slt, index_formula_id_opt, index_formula_id_slt_type)
    query_vectors = sum_queries(query_vectors_slt, query_vectors_opt, query_vectors_slt_type)
    retrieval_result = retrieval(tensor_values, index_formula_id, query_vectors)
    TangentCFTBackEnd.create_result_file(retrieval_result, "cft_res", "cft_1")


if __name__ == "__main__":
    main()
