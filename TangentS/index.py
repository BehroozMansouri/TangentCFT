"""
    Tangent
    Copyright (c) 2013, 2015 David Stalnaker, Richard Zanibbi, Nidhin Pattaniyil, 
                  Andrew Kane, Frank Tompa, Kenny Davila Castellanos

    This file is part of Tangent.

    Tanget is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Tangent is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Tangent.  If not, see <http://www.gnu.org/licenses/>.

    Contact:
        - Richard Zanibbi: rlaz@cs.rit.edu
"""
import os
from concurrent.futures import ProcessPoolExecutor
import csv
import multiprocessing
import sys
import codecs
import time


from TangentS.utility.Stats import Stats
#from TangentS.math_tan.version03_index import Version03Index
from TangentS.math_tan.math_extractor import MathExtractor
from TangentS.utility.control import Control
from TangentS.math_tan.math_document import MathDocument
#from symbol_tree import SymbolTree
#from Tan
#from multiprocessing import Lock
sys.setrecursionlimit(10000)
from sys import argv, exit
import math_tan

"""
Indexer is a standalone script that indexes a collection

Supports mathml,.xhtml and tex files
"""

def print_help_and_exit():
    """
    Prints usage statement
    """

    print("Usage: python index.py [<cntl-file>] or python index.py help")
    print("       default <cntl-file> is tangent.cntl")
    print()
    print("where <cntl-file> is a tsv file that contains a list of parameter-value pairs")
    print("and must include at least the following entries:")
    print("     doc_list\\t<doc-id mapping file name>")
    print("and may optionally include:")
    print("     window\\t<window-size>")
    print("     chunk_size\\t<chunk_size>")
    print("           number of documents per batch, default=200")
    print("as well as other pairs.")
    print("N.B. index.py will update <cntl-file> to also include:")
    print("     cntl, file_skips, and index_fileids.")
    exit()


def read_file(filename, file_id, semantic, missing_tags=None, problem_files=None):
    """
    Read file for parsing

    :type filename: string
    :param filename: file to be parsed

    :rtype: list(SymbolTree)
    :return list of Symbol trees found in the file
    """
    #s = time.time()
    (ext,content) = MathDocument.read_doc_file(filename)

    if ext == '.tex' and not semantic:
        t = MathExtractor.parse_from_tex(content, file_id)
        #print("file %s took %s"%(file_id,time.time()-s))
        return [t], 0
    elif ext in {'.xhtml', '.mathml', '.mml', '.html'}:
        t, n_err = MathExtractor.parse_from_xml(content, file_id, operator=semantic, missing_tags=missing_tags,
                                                problem_files=problem_files)
        #print("file %s took %s per expr"%(file_id,(time.time()-s)/len(t)))
        for item in t:
            #slttuplesList = SymbolTree.get_pairs(item, window='all')
            print(item)
        return t, n_err
    else:
        if ext == '.tex' and semantic:
            if "invalid_filetype" not in problem_files:
                problem_files["invalid_filetype"] = set([filename])
            else:
                problem_files["invalid_filetype"].add(filename)

            print('invalid file format %s for %s in operator tree mode' % (ext, filename))
        else:
            problem_files["unknown_filetype"] = problem_files.get("unknown_filetype", set())
            problem_files["unknown_filetype"].add(filename)
            print('Unknown filetype %s for %s' % (ext, filename))
        return [], 0

def read_file_behrooz(filename, file_id, semantic, missing_tags=None, problem_files=None):
    """
    Read file for parsing

    :type filename: string
    :param filename: file to be parsed

    :rtype: list(SymbolTree)
    :return list of Symbol trees found in the file
    """
    #s = time.time()
    (ext,content) = MathDocument.read_doc_file(filename)
    t = MathExtractor.Behrooz_parse_from_xml(content, 1, window=3, operator=semantic, missing_tags=missing_tags,
                                                problem_files=problem_files)
        # #print("file %s took %s per expr"%(file_id,(time.time()-s)/len(t)))
        # for item in t:
        #     #slttuplesList = SymbolTree.get_pairs(item, window='all')
        #     print(item)
    return t


# def math_indexer_task(pargs):
#     """
#     creates index tuples for the expressions in this subcollection
#     :param pargs:
#     :return: (fileid, combined_stats)
#     """
#     math_index, cntl, chunkid = pargs
#     combined_stats = Stats()
#
#     docs = MathDocument(cntl)
#
#     (chunk_size, mappings) = docs.read_mapping_file(chunkid)
#     combined_stats.num_documents += len(mappings)
#
#     semantic_trees = cntl.read("tree_model", num=False, default="layout").lower() == "operator"
#
#     seen_docs = []  # just dump them as they come
#     for (doc_id, filename) in enumerate(mappings,start=chunkid*chunk_size):
# ##        print('parsing %s, id:%s ' % (filename, doc_id),flush=True)
#
#         try:
#             # get all the symbol trees found in file
#             doc_trees, n_error = read_file(filename, doc_id, semantic_trees, missing_tags=combined_stats.missing_tags,
#                                            problem_files=combined_stats.problem_files)
#             combined_stats.expressions_with_e += n_error
#
#             for tree in doc_trees:
#                 combined_stats.num_expressions += 1
#                 combined_stats.global_expressions += len(tree.position)
#
#                 # pairs = tree.get_pairs(window) do not store pairs -- will be created in C++ module
#                 seen_docs.append(tree)
#         except Exception as err:
#             reason = str(err)
#             print("Failed to process document "+reason + "\n" + filename + "\n", file=sys.stderr)
#             combined_stats.problem_files[reason] = combined_stats.problem_files.get(reason, set())
#             combined_stats.problem_files[reason].add(doc_id)
#
#     fileid = math_index.add(seen_docs)
#     print("%s is done saving to database %s" % (chunkid,fileid), flush=True)
#
#     return fileid, combined_stats
#
#




def ConvertWikipediaToSLTTuplesNewVersion(filePathForresults, filename, dirId, lst, missing_tags=None, problem_files=None):
    try:
        parts = filename.split('/')
        file_name = os.path.splitext(parts[len(parts)-1])[0]
        # parts = parts[len(parts)-1].split(".")
        # FileID = parts[0]
        # for i in range (1,len(parts)-1):
        #     FileID = FileID + "."+parts[i]
        (ext, content) = MathDocument.read_doc_file(filename)
        formulas = MathExtractor.parse_from_xml(content, 1, operator=False, missing_tags=missing_tags,
                                                problem_files=problem_files)



        # formulas = MathExtractor.parse_from_xml(content,1, operator=False, missing_tags=missing_tags,problem_files=problem_files)

        #formulas = MathExtractor.behrooz_parse_from_xml(content=content, content_id=1, operator=True, missing_tags=missing_tags)
        for key in formulas:
            tuples = formulas[key].get_pairs(window=1, eob=True)
            if not tuples:
                return
            f = open(filePathForresults+"/"+str(dirId)+"/"+file_name+":"+str(key)+".txt", "w+")
            for t in tuples:
                f.write(t + "\n")
            f.close()

            #fileP = filePathForresults + "/" + str(dirId) + "/" + FileID + ":" + str(key) + ".txt"
            #f = open(fileP, "w+")
            #for t in tuples:
                #f.write(t+"\n")
            #f.close()

    except:
        print(filename)


    #
    # formulas = MathExtractor.Behrooz_parse_from_xml(content, 1, window=2, operator=None, missing_tags=missing_tags,
    #                                          problem_files=problem_files)
    # parts = filename.split('/')
    # parts = parts[len(parts)-1].split(".")
    # FileID = parts[0]
    # for i in range (1,len(parts)-1):
    #     FileID = FileID + "."+parts[i]
    # # formulas = MathExtractor.parse_from_xml_newVersion_FastText(content, 1, missing_tags=missing_tags,
    # #                                                             problem_files=problem_files)
    # for formula in formulas:
    #     if len(formulas.get(formula)) > 0:
    #         fileP = filePathForresults+"/"+str(dirId)+"/"+FileID+":"+str(formula)+".txt"
    #         f = open(fileP, "w+")
    #         for slttuple in formulas.get(formula):
    #             f.write(slttuple+"\n")
    #         f.close()
    # return formulas





def behrooztest():
    root = '/home/bm3302/Downloads/NTCIR12_MathIR_WikiCorpus_v2.1.0/NTCIR12_MathIR_WikiCorpus_v2.1.0/MathTagArticles/wpmath00000'
    filePathForresults = '/home/bm3302/FastText/SLTTuples_W1'
    lst = []
    for j in range(1, 17):
        tempAddress = root
        if j < 10:
            tempAddress = tempAddress + '0' + str(j) + '/Articles'
        else:
            tempAddress = tempAddress + str(j) + '/Articles'
        for filename in os.listdir(tempAddress):
            filePath = tempAddress + '/' + filename
            ConvertWikipediaToSLTTuplesNewVersion(filePathForresults, filePath, j,lst)
            # return
            # except Exception as err:
            #     print('-------------------------------------------\n' + str(err))
    for temp in lst:
        print(temp)


def behrooz_queryPreparation(filename, resultFile, file_id, missing_tags=None, problem_files=None):
    (ext, content) = MathDocument.read_doc_file(filename)
    #formulas = MathExtractor.parse_from_xml(content,1, operator=False, missing_tags=missing_tags,problem_files=problem_files)
    formulas = MathExtractor.parse_from_xml(content, 1, operator=False, missing_tags=missing_tags,
                                            problem_files=problem_files)
    for key in formulas:
        tuples = formulas[key].get_pairs(window=1, eob=True)
        if not tuples:
            return
        f = open(resultFile, "w+")
        for t in tuples:
            f.write(t+"\n")
        f.close()


def convertHTMLTOSLTprepareQueryForTest():

    for i in range(1, 21):
            print(i)
            behrooz_queryPreparation("/home/bm3302/Downloads/NTCIR12_MathIR_WikiCorpus_v2.1.0/TestQueries/"+str(i)+".html",
                                 "/home/bm3302/FastText/SLTTuples_W1/Queries/"+str(i)+".txt", 1)
        # except:
        #     print(i)
   #          "/home/bm3302/Downloads/NTCIR12_MathIR_WikiCorpus_v2.1.0/TestQueries/" + str(i) + ".html",
   #          '/home/bm3302/FastText/OPTTuples_W1/Queries/' + str(i) + ".txt", i)

    # doc_trees1 = read_file_behrooz('/home/bm3302/Downloads/NTCIR12_MathIR_WikiCorpus_v2.1.0/NTCIR12_MathIR_WikiCorpus_v2.1.0/MathTagArticles/wpmath0000004/Articles/Cesàro_summation.html', 1, None)
    # doc_trees = read_file_behrooz("/home/bm3302/Downloads/NTCIR12_MathIR_WikiCorpus_v2.1.0/TestQueries/32.html", 1, None)
    # doc_trees = read_file_behrooz("/home/bm3302/Downloads/NTCIR12_MathIR_WikiCorpus_v2.1.0/TestQueries/33.html", 1, None)
    # doc_trees = read_file_behrooz("/home/bm3302/Downloads/NTCIR12_MathIR_WikiCorpus_v2.1.0/TestQueries/34.html", 1, None)

# def behrooz_queryPreparation(filename, resultFile, file_id,window, missing_tags=None, problem_files=None):
#     # s = time.time()
#     (ext, content) = MathDocument.read_doc_file(filename)
#     t = MathExtractor.Behrooz_parse_from_xml(content, file_id, window=1, operator=None, missing_tags=missing_tags,
#                                              problem_files=problem_files)
#
#     for item in t:
#
#          print(item)
#     return t
#     (ext, content) = MathDocument.read_doc_file(filename)
#
#     if ext in {'.xhtml', '.mathml', '.mml', '.html'}:
#         #try:
#         formulas = MathExtractor.parse_from_xml(content, file_id, missing_tags=missing_tags, problem_files=problem_files)
#         if formulas:
#             for formula in formulas:
#                 slttuplesList = SymbolTree.get_pairs(formula, window='all')
#
#
#                 if len(slttuplesList) >= 1:
#                     # print("\n new formula" + str(formulaId))
#                     f = open(resultFile, "w+")
#                     for slttuple in slttuplesList:
#                         f.write(slttuple + "\n")
#                     f.close()
#         # print("file %s took %s per expr"%(file_id,(time.time()-s)/len(t)))
#         return formulas
#         # except:
#         #     return []
#     else:
#         problem_files["unknown_filetype"] = problem_files.get("unknown_filetype", set())
#         problem_files["unknown_filetype"].add(filename)
#         print('Unknown filetype %s for %s' % (ext, filename))
#         return []

def testFile():
    root = '/home/bm3302/Downloads/NTCIR12_MathIR_WikiCorpus_v2.1.0/NTCIR12_MathIR_WikiCorpus_v2.1.0/MathTagArticles/wpmath00000'
    count = 0
    for j in range(1, 17):
        tempAddress = root
        if j < 10:
            tempAddress = tempAddress + '0' + str(j) + '/Articles'
        else:
            tempAddress = tempAddress + str(j) + '/Articles'
        for filename in os.listdir(tempAddress):
            try:
                filePath = tempAddress + '/' + filename
                f = open (filePath)
                temp =""
                for line in f.readlines():
                    temp+= (line.strip())
                f.close()

                # if "<msup><mi>x</mi><mn>2</mn></msup>" in temp:
                #if "<semantics><mrow><msub><mi>x</mi><mi>a</mi></msub></mrow>" in temp:
                if "<semantics><mrow><mi>x</mi><mo>+</mo><mi>m</mi></mrow>" in temp:
                    print(filePath)
                # (ext, content) = MathDocument.read_doc_file(filePath)
                # # if "<mn>\n  " in content:
                # if "x^2" in content:
                #     print(filePath)
                    # return
            except:
                print('-------------------------------------------' + filename)


def check_value_exists():
    root = '/home/bm3302/Downloads/NTCIR12_MathIR_WikiCorpus_v2.1.0/NTCIR12_MathIR_WikiCorpus_v2.1.0/MathTagArticles/wpmath00000'
    for j in range(1, 17):
        tempAddress = root
        if j < 10:
            tempAddress = tempAddress + '0' + str(j) + '/Articles'
        else:
            tempAddress = tempAddress + str(j) + '/Articles'
        for filename in os.listdir(tempAddress):
            try:
                filePath = tempAddress + '/' + filename
                (ext, content) = MathDocument.read_doc_file(filePath)
                # if "<mn>\n  " in content:
                if "9.80665" in content:
                    print(filePath)
                    # return
            except:
                print('-------------------------------------------' + filename)

def main():
    # (ext, content) = MathDocument.read_doc_file("/home/bm3302/opt_test.html")
    # formulas = MathExtractor.parse_from_xml(content, 1, operator=True, missing_tags=None,
    #                                          problem_files=None)
    # for key in formulas:
    #     tuples = formulas[key].get_pairs(window=2, eob=True)
    #     for t in tuples:
    #         print(t + "\n")
        #f.close()
    # print(content)
    # formulas = MathExtractor.Behrooz_parse_from_xml(content, 1, window=2, operator=None)
    #
    # for formula in formulas:
    #     if len(formulas.get(formula)) > 0:
    #
    #         for slttuple in formulas.get(formula):
    #             print(slttuple)
    # return formulas
    # testFile()
    # if 1==1:
    #     return
    # root = '/home/bm3302/Downloads/NTCIR12_MathIR_WikiCorpus_v2.1.0/NTCIR12_MathIR_WikiCorpus_v2.1.0/MathTagArticles/wpmath0000010/Articles/(1-hydroxycyclohexan-1-yl)acetyl-CoA_lyase.html'
    # filePathForresults = '/home/bm3302/FastText/OPTTuples_W2'
    # ConvertWikipediaToSLTTuplesNewVersion(filePathForresults,root,10)
    #
    #
    # (ext, content) = MathDocument.read_doc_file(root)
    # formulas = MathExtractor.parse_from_xml(content, 1, operator=True, missing_tags=None,
    #                                         problem_files=None)
    # for key in formulas:
    #     tuples = formulas[key].get_pairs(window=2, eob=True)
    #     print(tuples)
    #count = 0
    #'/home/bm3302/Downloads/NTCIR12_MathIR_WikiCorpus_v2.1.0/NTCIR12_MathIR_WikiCorpus_v2.1.0/MathTagArticles'
    #check_value_exists()




# filePath = "E:/NTCIR-12_MathIR_Wikipedia_Corpus/wpmath0000002/Z-buffering.html"
#         (ext, content) = MathDocument.read_doc_file(filePath)
#         formulas = MathExtractor.parse_from_xml(content,1, operator=True, missing_tags=None,problem_files=None)
#         for key in formulas:
#             print("-------------------------------------------------------")
#             tuples = formulas[key].get_pairs(window=1, eob=True)
#             if not tuples:
#                 return
#         #f = open(resultFile, "w+")
#             for t in tuples:
#                 print(t+"\n")










    # temp = "E:/NTCIR-12_MathIR_Wikipedia_Corpus/wpmath0000002/"
    # for filePath in os.listdir("E:/NTCIR-12_MathIR_Wikipedia_Corpus/wpmath0000002"):
    #     (ext, content) = MathDocument.read_doc_file(temp+filePath)
    #     formulas = MathExtractor.parse_from_xml(content,1, operator=True, missing_tags=None,problem_files=None)
    #     for key in formulas:
    #         print("-------------------------------------------------------")
    #         tuples = formulas[key].get_pairs(window=1, eob=True)
    #         if not tuples:
    #             print (filePath)
    #         for t in tuples:
    #             parts = t.split("\t")
    #             for part in parts:
    #                 if part.count("!")==2:
    #                     print(filePath)
    #                     return
    # counter = 1
    # (ext, content) = MathDocument.read_doc_file("E:/NTCIR-12_MathIR_Wikipedia_Corpus/wpmath0000002/3D_projection.html")
    # formulas = MathExtractor.parse_from_xml(content,1, operator=True, missing_tags=None,problem_files=None)
    # for key in formulas:
    #     print("-------------------------------------------------------")
    #     print(counter)
    #     counter+=1
    #     tuples = formulas[key].get_pairs(window=1, eob=True)
    #     for t in tuples:
    #         print(t)






    convertHTMLTOSLTprepareQueryForTest()
    behrooztest()





    #
    # if 1==1:
    #     return
    #
    # if sys.stdout.encoding != 'utf8':
    #   sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer, 'strict')
    # if sys.stderr.encoding != 'utf8':
    #   sys.stderr = codecs.getwriter('utf8')(sys.stderr.buffer, 'strict')
    #
    # if (len(argv) > 2 or (len(argv) == 2 and argv[1] == 'help')):  # uses control file to control all parameters
    #     print_help_and_exit()
    # else:
    #     start = time.time()
    #     try:
    #         cntl = Control(argv[1]) if len(argv) == 2 else Control()
    #     except Exception as err:
    #         print("Error in reading <cntl-file>: " +str(err))
    #         print_help_and_exit()
    #
    #     doc_id_mapping_path = cntl.read("doc_list")
    #     if not doc_id_mapping_path:
    #         print("<cntl-file> missing doc_list")
    #         print_help_and_exit()
    #     window = cntl.read("window",num=True)
    #     if window and window < 1:  # window values smaller than 2 make no sense
    #         print('Window values smaller than 1 not permitted -- using 1')
    #         window = 1
    #     chunk_size = cntl.read("chunk_size",num=True,default=200)
    #
    #     print("reading %s" % doc_id_mapping_path, flush=True)
    #     mappings = []
    #     filepos = []
    #
    #     num_docs = 0
    #     row = "-"
    #     with open(doc_id_mapping_path, newline='', encoding='utf-8') as mapping_file:
    #         while True:
    #             if num_docs % chunk_size == 0:
    #                 filepos.append(mapping_file.tell())
    #             num_docs += 1
    #             row = mapping_file.readline()
    #             if row == "":
    #                 num_docs -= 1
    #                 if num_docs % chunk_size == 0:
    #                     del filepos[-1]
    #                 break
    #     cntl.store("file_skips",str(filepos))
    #
    #     print("There are " + str(num_docs) + " documents to index", flush=True)
    #     combined_stats = Stats()
    #
    #     if num_docs > 0:
    #         math_index = Version03Index(cntl, window=window)
    #
    #         max_jobs = min(10,num_docs)
    #         manager = multiprocessing.Manager()
    #         lock = manager.Lock()
    #
    #         #identify chunks to be indexed by each process
    #         args = [(math_index, cntl, chunkid) for chunkid in list(range(len(filepos)))]
    #
    #         fileids = set()
    #
    #         with ProcessPoolExecutor(max_workers=max_jobs) as executor:
    #
    #             # single process .. .for debugging ...
    #             #for fileid, stats in map(math_indexer_task, args):
    #             for fileid, stats in executor.map(math_indexer_task, args):
    #                 fileids.add(fileid)
    #                 combined_stats.add(stats)
    #
    #         for fileid in fileids:
    #             math_index.closeDB(fileid, mode="i")
    #         cntl.store("index_fileids",str(fileids))
    #
    #     print("Done indexing collection %s" % (doc_id_mapping_path))
    #     combined_stats.dump()
    #
    #     cntl.dump()  # output the revised cntl file
    #
    #     end = time.time()
    #     elapsed = end - start
    #
    #     print("Elapsed time %s" % (elapsed))

if __name__ == '__main__':
   main()