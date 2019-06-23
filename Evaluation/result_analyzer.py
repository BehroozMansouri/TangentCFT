import subprocess
import os.path


def results_by_parameters(retrieval_id, result_file_path):
    retrieval_file = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'Retrieval_Results/res_'))+str(retrieval_id)
    result_file = open(result_file_path, "w")
    map_partial = {}
    map_full = {}
    process_name = "trec_eval"
    judge_file = "judge.dat"
    result_file.write("query_id, partial_bpref, full_bpref\n")

    temp = subprocess.check_output([process_name, judge_file, retrieval_file, "-l1", "-q"])
    temp = temp.decode("utf-8").split("\n")
    for item in temp:
        if str.startswith(item, "bpref"):
            score = item.split("\t")[2]
            id = item.split("\t")[1]
            if id == "all":
                query_id = id
            else:
                query_id = id.split("-")[2]
            map_partial[query_id] = score

    temp = subprocess.check_output([process_name, judge_file, retrieval_file, "-q", "-l3"])
    temp = temp.decode("utf-8").split("\n")
    for item in temp:
        if str.startswith(item, "bpref"):
            score = item.split("\t")[2]
            id = item.split("\t")[1]
            if id=="all":
                query_id = id
            else:
                query_id = id.split("-")[2]
            map_full[query_id] = score

    for key in map_full:
        result_file.write(str(key) + "," + str(map_partial[key]) + "," + str(map_full[key])+"\n")
    result_file.close()

results_by_parameters(7090, "results.csv")