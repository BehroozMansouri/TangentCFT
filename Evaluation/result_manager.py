import subprocess
import os.path
from Configuration.configuration import configuration


def main():

    id_1 = 7061#int(argv[1])
    id_2 = 7064#int(argv[2])
    "file path to save the result of the analysis"
    result_file_path = "result6.csv"#argv[3]
    results_by_parameters(id_1, id_2, result_file_path)


def results_by_parameters(start_file_id, end_file_id, result_file_path):
    result_file = open(result_file_path, "w")
    process_name = "trec_eval"
    judge_file = "judge.dat"
    config = configuration("config/config_" + str(start_file_id))
    dic = config.__dict__
    result_file.write("file_id,")
    for val in dic:
        result_file.write(str(val) + ",")
    result_file.write("partial_bpref, full_bpref\n")
    for file_id in range(start_file_id, end_file_id + 1):
        result_file_name = "Retrieval_Results/res_" + str(file_id)
        if not os.path.isfile(result_file_name):
            continue
        temp = subprocess.check_output(
            [process_name, judge_file, result_file_name, "-l1"])
        partial_bpref = temp.decode("utf-8").split("\n")[8].split("\t")[2]

        temp = subprocess.check_output(
            [process_name, judge_file, result_file_name, "-l3"])
        full_bpref = temp.decode("utf-8").split("\n")[8].split("\t")[2]
        config = configuration("config/config_" + str(file_id))
        dic = config.__dict__
        result_file.write(str(file_id) + ",")
        for val in dic.values():
            result_file.write(str(val) + ",")
        result_file.write(str(partial_bpref) + "," + str(full_bpref) + "\n")
    result_file.close()


if __name__ == "__main__":
    main()
