__author__ = 'KDavila, FWTompa'

import os
from TangentS.ranking.query import Query
from TangentS.utility.text_query import TQuery
from TangentS.utility.comp_query import CompQuery
from TangentS.math_tan.math_document import MathDocument

class ReadResults:
    @classmethod
    def read_math_results(cls,input_filename,doc_list):

        """
        :param input_filename: output of core engine or reranked math_tan results
        :type  input_filename: string
        :return: query responses
        :rtype:  dict mapping query_name -> CompQuery()
        """

        in_file = open(input_filename, 'r', encoding="utf-8")
        print("Opened " + input_filename,flush=True)
        lines = in_file.readlines()
        in_file.close()

        print("Reading " + str(len(lines)) + " lines of input",flush=True)
        current_name = None
        all_queries = {}

        for idx, line in enumerate(lines):
##            print(str(idx) + line, flush=True)
            parts = line.strip().split("\t")

            if len(parts[0]) == 0:
                # do nothing
                nothing = None
            elif len(parts) == 2:
                if parts[0][0] == "Q":
                    current_name = parts[1]
                    try:
                        current_query = all_queries[current_name]
                    except:
                        current_query = CompQuery(current_name)
                        all_queries[current_name] = current_query
                    current_expr = None
                elif parts[0][0] == "E":
                    if current_name is None:
                        print("Invalid expression at " + str(idx) + ": Q tuple with query name expected first", flush=True)
                    else:
                        query_expression = parts[1]
                        current_expr = Query(current_name,query_expression)
                        current_query.add_expr(current_expr)
                elif parts[0][0] == "C":
                    print("Constraint at " + str(idx) + " ignored: " + line)

            elif len(parts) == 3 and parts[0][0] == "I":
                if current_name is None or current_expr is None:
                    print("Invalid information at " + str(idx) + ": Q tuple with query name and E tuple with expression expected first")
                elif parts[1] == "qt":
                    current_expr.initRetrievalTime = float( parts[2] )
                elif parts[1] == "post":
                    current_expr.postings = int( parts[2] )
                elif parts[1] == "expr":
                    current_expr.matchedFormulae = int( parts[2] )
                elif parts[1] == "doc":
                    current_expr.matchedDocs = int( parts[2] )

            elif len(parts) == 5 and parts[0][0] == "R":
                if current_name is None or current_expr is None:
                    print("Invalid result item at " + str(idx) + ": Q tuple with query name and E tuple with expression expected first")
                else:
                    doc_id = int(parts[1])
                    doc_name = doc_list.find_doc_file(doc_id)
                    if not doc_name:
                        doc_name = "NotADoc"
                    location = int(parts[2])
                    expression = parts[3]
                    score = float(parts[4])
                    current_expr.add_result(doc_id, doc_name, location, expression, score)

            else:
                print("Ignoring invalid tuple at " + str(idx) + ": " + line)
        print("Read " + str(len(all_queries)) + " queries",flush=True)
        return all_queries
 
    @classmethod                 
    def add_text_results(cls,all_queries,input_filename,doc_list):

        """
        :param all_queries: results from querying math_tan expressions
        :type  all_queries: dict mapping query_name -> CompQuery()
        :param input_filename: output of text engine
        :type  input_filename: string
        """

        in_file = open(input_filename, 'r', encoding="utf-8")
        print("Opened " + input_filename,flush=True)
        lines = in_file.readlines()
        in_file.close()

        print("Reading " + str(len(lines)) + " lines of input",flush=True)
        current_name = None

        for idx, line in enumerate(lines):
            parts = line.strip().split("\t")

            if len(parts[0]) == 0:
                # do nothing
                nothing = None
            elif len(parts) == 2:
                if parts[0][0] == "Q":
                    current_name = parts[1]
                    current_tquery = TQuery(current_name)
                    try:
                        current_query = all_queries[current_name]
                    except:  # no matching query name for math_tan expressions ???
                        print("No math_tan results found for query name " + current_name)
                        current_query = CompQuery(current_name)
                        all_queries[current_name] = current_query
                    current_query.set_keywords(current_tquery)
                elif parts[0][0] == "P":
                    if current_name is None:
                        print("Invalid keyword at " + str(idx) + ": Q tuple with query name expected first")
                    else:
                        current_tquery.add_keyword(parts[1])
                    
##            elif len(parts) == 3 and parts[0][0] == "I":
##                if current_name is None:
##                    print("Invalid information item at " + str(idx) + ": Q tuple with query name expected first")
##                elif parts[1] == "qt":
##                    current_expr.initRetrievalTime = float( parts[2] )
##                elif parts[1] == "post":
##                    current_expr.postings = int( parts[2] )
##                elif parts[1] == "expr":
##                    current_expr.matchedFormulae = int( parts[2] )
##                elif parts[1] == "doc":
##                    current_expr.matchedDocs = int( parts[2] )

            elif len(parts) == 3 and parts[0][0] == "M":
                if current_name is None:
                    print("Invalid result item at " + str(idx) + ": Q tuple with query name expected first")
                else:
                    doc_id = int(parts[1])
                    doc_name = doc_list.find_doc_file(doc_id)
                    if not doc_name:
                        doc_name = "NotADoc"
                    score = float(parts[2])
                    current_tquery.add_result(doc_id, doc_name, score)

            else:
                print("Ignoring invalid tuple at " + str(idx) + ": " + line)
