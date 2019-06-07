from subprocess import check_output
import operator
from sys import argv

def createJudgeFile():
    "the main judge file"
    judgefilepath = "/home/bm3302/FastText/ResultFiles/judge3.dat"

    "creating judge files with exception of query left out of the fold"
    judgedirectory = "/home/bm3302/FastText/Judges/judge"

    for i in range(1, 21):
        file = open(judgedirectory+str(i)+".txt", "+w")
        main_judge_file = open(judgefilepath)
        line = main_judge_file.readline()
        while line:
            line = line.rstrip('\n')
            queryId = int(line.split(" ")[0].split("-")[2])
            if i != queryId:
                file.write(line+"\n")
            line = main_judge_file.readline()
        file.close()
        main_judge_file.close()

def trecEval(judge_filepath, combined_result):
    output = check_output(["trec_eval", judge_filepath, combined_result, "-l1"])
    output = output.decode('utf-8')
    items = output.split("\n")
    partial_bpref = float(items[8].split("\t")[2])

    output = check_output(["trec_eval", judge_filepath, combined_result, "-l3"])
    output = output.decode('utf-8')
    items = output.split("\n")
    full_bpref = float(items[8].split("\t")[2])

    return partial_bpref, full_bpref

'This method takes one of the result of embedding file path and' \
' for each query creates a map of doc with their related cosine sim score'

def ReadResultFile(result_filepath):
    result = {}
    with open(result_filepath) as fp:
        line = fp.readline()
        while line:
            line = line.strip("\n")
            parts = line.split(" ")
            queryid = int(parts[0].split("-")[2])
            if queryid > 20:
                line = fp.readline()
                continue
            doc = parts[2]
            score = float(parts[4])
            map = {}
            if queryid in result:
                map = result[queryid]
            map[doc] = score
            result[queryid] = map
            line = fp.readline()
    for key in result.keys():
        map = result[key]
        min_val = min(map.values())
        max_val = max(map.values())
        temp = (max_val-min_val)
        if temp == 0:
            temp = 1
        for item in map.keys():
            if (temp == 1):
                map[item] = 1
            else:
                map[item] = (map[item]-min_val) / temp
        result[key] = map
    return result



def threeResultCombination(map1, map2, query_id, alpha, betha):
    doc_score_map = {}
    res_1 = map1[query_id]
    res_2 = map2[query_id]
    for key in res_1:
        if key in res_2:
            doc_score_map[key] = (alpha * res_1[key])+(betha*res_2[key])
        else:
            doc_score_map[key] = (alpha * res_1[key])
    for key in res_2:
        if key not in res_1:
                doc_score_map[key] = (betha * res_2[key])

    sorted_judgeMap = sorted(doc_score_map.items(), key=operator.itemgetter(1))
    sorted_judgeMap.reverse()
    return sorted_judgeMap[0:1000]

def combineFiles(alpha,beta, res1, res2, foldId):
    resultfilepath = "/home/bm3302/FastText/ResultFiles/temp_combined_"+str(foldId)+".txt"
    query_doc_score_map = {}
    for query_id in range(1, 21):
        query_doc_score_map[query_id] = threeResultCombination(res1, res2, query_id,alpha,beta)
    f = open(resultfilepath, "w+")
    for query_id in query_doc_score_map:
        map = query_doc_score_map[query_id]
        count = 1
        for item in map:
            f.write("NTCIR12-MathWiki-" + str(query_id) + " " + "xxx " + item[0] + " " + str(count) + " " + str(
                item[1]) + " RunCombine3\n")
            count += 1
    f.close()
    return resultfilepath

def twoResultCombination(map1, map2, query_id,alpha):
    doc_score_map = {}
    res_1 = map1[query_id]
    res_2 = map2[query_id]
    for key in res_1:
        if key in res_2:
            doc_score_map[key] = (alpha * res_1[key])+((1-alpha)*res_2[key])
        else:
             doc_score_map[key] = (alpha * res_1[key])
    for key in res_2:
        if key not in res_1:
                doc_score_map[key] = ((1-alpha)*res_2[key])


    sorted_judgeMap = sorted(doc_score_map.items(), key=operator.itemgetter(1))
    sorted_judgeMap.reverse()
    return sorted_judgeMap[0:1000]

def combine2Files(alpha, res1, res2,foldId):
    resultfilepath = "/home/bm3302/FastText/ResultFiles/temp_combined_"+str(foldId)+".txt"
    query_doc_score_map = {}
    for query_id in range(1, 21):
        query_doc_score_map[query_id] = twoResultCombination(res1, res2, query_id,alpha)
    f = open(resultfilepath, "w+")
    for query_id in query_doc_score_map:
        map = query_doc_score_map[query_id]
        count = 1
        for item in map:
            f.write("NTCIR12-MathWiki-" + str(query_id) + " " + "xxx " + item[0] + " " + str(count) + " " + str(
                item[1]) + " RunCombine3\n")
            count += 1
    f.close()
    return resultfilepath

def kfold(foldId):
    filepath1 = "/home/bm3302/FastText/ResultFiles/Res_Top_626.txt"
    filepath2 = "/home/bm3302/FastText/ResultFiles/wei.dat"

    res1 = ReadResultFile(filepath1)
    res2 = ReadResultFile(filepath2)


    query_id = foldId
    print("fold"+str(query_id))
    alpha = 0.00


    # Insurance policy.
    fold_out = open("/home/bm3302/FastText/ResultFiles/FOLD_OUT_"+str(foldId)+".csv","+w")
    fold_out.write("Query,alpha,beta,partial,full,harmonic_mean\n")

    while alpha <= 1:
        beta = 1.0 - alpha
        combined_resultfile = combineFiles(alpha, beta, res1, res2, foldId)
        # These are *average* scores form TREC_EVAL.
        partial_bpref, full_bpref = trecEval("/home/bm3302/FastText/Judges/judge"+str(query_id)+".txt", combined_resultfile)
        harmonic_mean = (2 * partial_bpref * full_bpref) / (partial_bpref + full_bpref)

        # Insurance policy.
        iter_tuple = (foldId, alpha, 1.0 - alpha, partial_bpref, full_bpref, harmonic_mean)
        fold_out.write(','.join(map(str, iter_tuple)) + "\n")

        alpha += 0.01

    # Close the 'insurance' file (exhaustive record)
    fold_out.close()




def kfold2(foldId):
    filepath1 = "/home/bm3302/FastText/ResultFiles/Res_Top_34.txt"
    filepath2 = "/home/bm3302/FastText/ResultFiles/Res_Top_314.txt"
    res1 = ReadResultFile(filepath1)
    res2 = ReadResultFile(filepath2)


    file_result = open("/home/bm3302/FastText/ResultFiles/test_kfold_"+str(foldId)+".txt","+w")
    file_result.write("Query,alpha,partial,full,score\n")
    query_id = foldId
    print("fold"+str(query_id))
    alpha = 0.000

    fold_out = open("/home/bm3302/FastText/ResultFiles/FOLD2_OUT_" + str(foldId) + ".csv", "+w")
    fold_out.write("Query,alpha,beta,gamma,partial,full,harmonic_mean\n")

    while alpha <= 1:
        combined_resultfile = combine2Files(alpha, res1, res2, foldId)

        # These are *average* scores form TREC_EVAL.
        partial_bpref, full_bpref = trecEval("/home/bm3302/FastText/Judges/judge" + str(query_id) + ".txt",
                                             combined_resultfile)

        harmonic_mean = (2 * partial_bpref * full_bpref) / (partial_bpref + full_bpref)

        # Insurance policy.
        iter_tuple = (foldId, alpha, partial_bpref, full_bpref, harmonic_mean)
        fold_out.write(','.join(map(str, iter_tuple)) + "\n")
        alpha += 0.001
    # Close the 'insurance' file (exhaustive record)
    fold_out.close()

def main():
    #print(trecEval("/home/bm3302/FastText/ResultFiles/judge.dat","/home/bm3302/FastText/ResultFiles/tangent-s.dat"))
    #foldId = int(argv[1])
    for foldId in range(1,21):
        kfold(foldId)
if __name__ == '__main__':
    main()