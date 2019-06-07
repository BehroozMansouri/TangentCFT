import subprocess
import os.path

f = open("/home/bm3302/FastText/ResultFiles/results.txt", "w")
f.write("file_id,partial_bpref,full_bpref")

for file_id in range(1000,4000):
    result_file_name = "/home/bm3302/FastText/ResultFiles/Res_Top_"+str(file_id)+".txt"
    if not os.path.isfile(result_file_name):
        continue
    temp = subprocess.check_output(["trec_eval", "/home/bm3302/FastText/ResultFiles/judge3.dat", result_file_name, "-l1"])
    partial_bpref = temp.decode("utf-8").split("\n")[8].split("\t")[2]
    temp = subprocess.check_output(["trec_eval", "/home/bm3302/FastText/ResultFiles/judge3.dat", result_file_name, "-l3"])
    full_bpref = temp.decode("utf-8").split("\n")[8].split("\t")[2]
    f.write(str(file_id)+","+str(partial_bpref)+","+str(full_bpref)+"\n")

f.close()