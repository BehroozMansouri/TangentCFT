from sys import argv

import torch
import torch.nn.functional as F
import result_manager


def read_file_list(file_path_to_rerank):
    f = open(file_path_to_rerank)
    lst = []
    line = f.readline()
    while line:
        lst.append(line.split(" ")[2])
        line = f.readline()
    return lst

def re_rank_basedon_model(file_path_to_rerank, result_id, dimension):

    map_file_to_look = read_file_list(file_path_to_rerank)
    doc_id_map, doc_tensors = result_manager.read_specific_files("/home/bm3302/FastText/Run_Result_" + str(result_id), dimension, map_file_to_look)
    query_vector_map = result_manager.read_query_vectors("/home/bm3302/FastText/Run_Result_" + str(result_id) + "/Queries", dimension)

    f = open('/home/bm3302/FastText/ResultFiles/Res_Top1_' + str(result_id) + '.txt', 'w')
    for queryId in query_vector_map:
        query_vec = query_vector_map[queryId]

        dist = F.cosine_similarity(doc_tensors, query_vec)
        index_sorted = torch.sort(dist, descending=True)[1]
        top_1000 = index_sorted[:1000]

        top_1000 = top_1000.data.cpu().numpy()
        cos_values = torch.sort(dist, descending=True)[0][:1000].data.cpu().numpy()
        count = 1
        query = "NTCIR12-MathWiki-" + str(queryId)
        line = query + " xxx "
        for x in top_1000:
            doc_id = doc_id_map[x]
            score = cos_values[count - 1]
            temp = line + doc_id + " " + str(count) + " " + str(score) + " Run_" + str(result_id)
            f.write(temp + "\n")
            count += 1
    f.close()


def main(argv):
    value1 = int(argv[1])
    value2 = int(argv[2])
    dimension = int(argv[3])
    for result_id in range(value1, value2):
        re_rank_basedon_model("/home/bm3302/FastText/ResultFiles/Res_Top_436.txt", result_id, dimension)
        print("config File finished"+str(result_id))


if __name__ == '__main__':
    main(argv)