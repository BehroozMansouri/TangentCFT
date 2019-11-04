
__author__ = 'FWTompa'

import os

from TangentS.ranking.query import Query
from TangentS.utility.text_query import TQuery
from TangentS.math_tan.symbol_tree import SymbolTree
from TangentS.math_tan.layout_symbol import LayoutSymbol
#from TangentS.ranking.ranking_functions import similarity_v06, similarity_v09, similarity_v10, similarity_v11
from TangentS.ranking.reranker import Reranker
from TangentS.math_tan.math_document import MathDocument

class MathScore:

    def __init__(self, qexprnum, candidate):
        self.qexprnum = qexprnum
        self.candidate = candidate
        self.top_in_doc = 0

class CompQueryResult:          # results for a single document
    
    def __init__(self, doc_id, doc_name):
        self.doc_id = doc_id          # id of document
        self.doc_name = doc_name      # name of document
        self.mcombined = 0            # combined formula match score
        self.tscore = (0,0)           # keyword match score (raw,normalized)
        self.final_score = 0          # combined overall score
        self.mscores = []             # sequence of query number - Result tuples
        self.tpos = {}                # mapping of terms to text positions

    def add_mscore(self, qexpr, candidate):
        match = MathScore(qexpr, candidate)   # N.B. qexpr will repeat if more than one match in a document
        self.mscores.append(match)
    def set_tscore(self, tscore):
        self.tscore = tscore
    def set_tpos(self, tpos):
        self.tpos = tpos

class CompQuery:
    """
    CompQuery: name, mqueries, tquery, by_document, msorted_documents, sorted_documents, elapsed_time
    name: string
    mqueries: [Query]
        Query: name, mathml, tree, expression, results, documents, sorted_documents, sorted_document_index,
                constraints, sorted_results, sorted_result_index , sorted_abs_ranks, elapsed_time,
                initRetrievalTime, postings, matchedFormulae, matchedDocs, html_queryblock = {}
        results = {expression -> Result}
            Result: Query, expression, tree, original_ranking, original_score, mathml, new_scores, locations, matched_elements,
                    unified_elements, wildcard_matches, all_unified, times_rendered
            locations: [(docid, location)]
        documents: {docid -> doc_name}
    tquery: TQuery
        TQuery: name, results, keywords
            results: {docid -> (doc_name, (raw score, normalized score), tpos)}
            tpos: {term -> [position]}
            keywords: [string]
    by_document: {docname -> CompQueryResult}
        CompQueryResult: doc_id, doc_name, mscores, tscore, tpos, mcombined, final_score
        mscores: [MathScore]
            MathScore: qexprnum, candidate, top_in_doc
            qexprnum: int
            candidate: Result
        tscore: int
    msorted_documents: [CompQueryResult]
    sorted_documents: [CompQueryResult]
    """

    def __init__(self, name):
        self.name = name               # query identifier
        self.mqueries = []             # sequence of results per query formula
        self.tquery = None             # one result for keyword parts of query
        self.by_document = None        # pivoted results per document
        self.msorted_docs = []         # sorted docs by combined math_tan score
        self.sorted_docs = []          # sorted docs by combined math_tan and text score
        self.elapsed_time = 0.0        # total execution time

    def add_expr(self,mquery):
        """
        :param mquery: math_tan query results for one expression only
        :type  mquery: Query()
        """
        self.mqueries.append(mquery)

    def set_keywords(self,tquery):
        """
        :param tquery: text query results for collection of keywords
        :type  tquery: TQuery()
        """
        self.tquery = tquery

    def pivot_by_docs(self,how):
        # process all query results
        """
        how = "core" => use core value ranks directly
              "MSS" => use reranking scores
        """
        self.by_document = {}
##        intID = True        # CHANGED TO MATCH ON DOC NAME ALWAYS

        if self.tquery:
            for doc_id in self.tquery.results.keys():
##                try:
##                    intID = (int(doc_id) == doc_id) # True if doc_id is an integer
##                except:
##                    intID = False # otherwise need to match on filename
                (docname,score,positions) = self.tquery.results[doc_id]
                # add document if first time seen
                # join on docname, not doc_id
                try:
                    doc = self.by_document[docname]
                except:
                    doc = CompQueryResult(doc_id,docname)
                    self.by_document[docname] = doc
                # add score of keyword match to current document
                doc.set_tscore(score)
                doc.set_tpos(positions)
        if self.mqueries:

            # Reranker.CreateFromMetricID(...)
            # TODO: Adapt the code below to work under the new class design for the re-ranker
            raise Exception("Re-ranking math_tan expressions on combined queries not implemented")

            for qexprnum,query in enumerate(self.mqueries):
                # keep scores for all existing formulas over all documents
                for result in query.results.values():
                    # N.B. only one Result structure per matched formula expression
                    #print("Candidate: " + result.tree.tostring(), flush=True)

                    if how == "MSS": # compute the MSS score if requested
                        sim_res = similarity_v06(query.tree, result.tree, Query.create_default_constraints(query.tree))
                        result.new_scores = sim_res[0]  # scores returned as first component of result -- other components are node sets
                    elif how == "v09":
                        sim_res = similarity_v09(query.tree, result.tree, Query.create_default_constraints(query.tree))
                        result.new_scores = sim_res[0] # only use scores
                    elif how == "v10":
                        sim_res = similarity_v10(query.tree, result.tree, Query.create_default_constraints(query.tree))
                        result.new_scores = sim_res[0] # only use scores
                    elif how == "v11":
                        sim_res = similarity_v11(query.tree, result.tree, Query.create_default_constraints(query.tree))
                        result.new_scores = sim_res[0] # only use scores
                    else:
                        result.new_scores = [result.original_score]  # otherwise, just use original score
                        
                    for doc_id, offset in result.locations:
                        title = query.documents[doc_id]
                        #title = title.rpartition('\\')[2]    # just last part
                        title = os.path.basename(title) # just last part (KMD)

##                        if not intID: # join on title instead of doc_id
                        joiner = title

##                        else:
##                            joiner = doc_id
                        # add document if first time seen
                        try:
                            doc = self.by_document[joiner]
                            doc.doc_id = doc_id # prefer using math_tan ids (to match positions later)
                        except:
                            doc = CompQueryResult(doc_id,title)
                            self.by_document[joiner] = doc
                        # add current result to current document
                        doc.add_mscore(qexprnum,result)

    def combine_math(self,how, msize_norm):
        """
        how = "core" => use core value ranks directly
              "MSS" => use reranking scores
        """

        if self.by_document is None:
            self.pivot_by_docs(how)   # must pivot by documents before combining; compute MSS if need be

##        # old code using vector of formulae and reranking on all formulae at once          
##        if how == "rerank" and self.mqueries:  
##            
##            # use reranking on vector of queries to determine score
##            if len(self.mqueries) == 1:
##                qtree = self.mqueries[0].tree
##            else:
##                qtree = SymbolTree(MathSymbol.make_matrix(list(map(lambda x: x.tree.root,self.mqueries)),None))

        size_based_normalization = (msize_norm > 0)

        # precompute normalization based on query size
        mq_weight = []

        if size_based_normalization:
            # larger queries get larger weight
            alllength = 0.0

            qlens = []
            for i, q in enumerate(self.mqueries):
                qlens.append(q.expression.count("[")) # number of nodes is proxy for number of tuples
                alllength += qlens[i]

            for i in range(len(self.mqueries)):
                mq_weight.append(qlens[i] / alllength)
        else:
            # all queries weight the same ...
            for i in range(len(self.mqueries)):
                mq_weight.append(1.0 / len(self.mqueries))

        if how == "MSS":
            n_scores = 8
        elif how == "v11":
            n_scores = 3
        elif how == "v09" or how == "v10":
            n_scores = 5
        else:
            n_scores = 1

        for (doc_id,doc) in self.by_document.items():
            if not doc.mscores:  # no math_tan formula scores for the document
                doc.mcombined = [0.0] * n_scores
            else:
                # keep only the highest scoring match per qexpr
                matches = {}  # {qexprnum -> candidate}
                for mathscore in doc.mscores:
                    qexprnum = mathscore.qexprnum
                    try:
                        oldscore = matches[qexprnum]
                        if mathscore.candidate.new_scores > oldscore.candidate.new_scores:
                            matches[qexprnum] = mathscore
                            oldscore.top_in_doc = 0
                            mathscore.top_in_doc = 1 
                    except:
                        matches[qexprnum] = mathscore
                        mathscore.top_in_doc = 1

                # Use the weights computed previously
                allscore = [0.0] * n_scores
                for i,q in enumerate(self.mqueries):
                    if i in matches:
                        score = matches[i].candidate.new_scores

                        for j in range(len(score)):
                            allscore[j] += score[j] * mq_weight[i]

                # Set score
                doc.mcombined = allscore

##                elif how == "rerank":
##                    # use reranking on vector of queries against vector of matches       
##                    if len(self.mqueries) == 1:
##                        ctree = matches[0].tree
##                    else:
##                        # for each query in order, create item in vector of candidate matches in document
##                        # however, the result trees are shared among all documents having the same expression! need to duplicate first (by reparsing expression)     
##                        ctree = SymbolTree(MathSymbol.make_matrix(list(map(lambda i:SymbolTree.parse_from_slt(matches[i].expression).root if i in matches else MathSymbol("W!"),range(len(self.mqueries)))),None))
##                   sim_res = = similarity_v05(qtree, ctree, Query.create_default_constraints(qtree))
##                   doc.mcombined = sim_res[0]  # scores returned as first component of result -- others are node sets
##                else:
##                    print('Error: combine_math must be either "average" or "rerank", not "' + how + '"')
##                    return
                
            self.msorted_docs.append(doc)
        self.msorted_docs.sort(key=lambda doc: doc.mcombined,reverse=True)


    def combine_math_text(self,rerank,mweight, mdynamic, msize_norm, mtext_only):
        """
        how = "average" => simple weighted average with qexpr as weight
              "rerank" => use reranking on vector of expressions
        :param mweight: percentage of weight to put on math_tan score (rest on text score)
        :type  mweight: int
        """
        if mtext_only > 0:
            mweight = 0.0
        else:
            dynamic_weights = (mdynamic > 0)

            if dynamic_weights:
                # do it dynamically based on proportion Keywords/Expressions
                if self.tquery:
                    n_keywords = len(self.tquery.keywords)
                else:
                    n_keywords = 0

                query_elements = len(self.mqueries) + n_keywords
                mweight = len(self.mqueries) / float(query_elements)
            else:
                # use values provided ...
                mweight = mweight/100.0 # convert to fraction in 0..1

        tweight = 1 - mweight

        if not self.msorted_docs:
            self.combine_math(rerank, msize_norm)   # must combine math_tan scores first
            
        for doc in self.msorted_docs:
            mscore = doc.mcombined[0]
            doc.final_score = [mweight * float(mscore) + tweight * float(doc.tscore[1] if self.tquery.keywords else 1.0)] # use normalized text score
            doc.final_score += doc.mcombined[1:]

            self.sorted_docs.append(doc)
        self.sorted_docs.sort(key=lambda doc: doc.final_score,reverse=True)
        
    def get_math_pos(self, doc):
        pos = []
        for expr in doc.mscores:
            if expr.top_in_doc:
                for loc in expr.candidate.locations:
                    if loc[0] == doc.doc_id: # all doc offsets for the identical formula are listed
                        pos.append(loc[1])
        return(pos)

    def get_math_pos_with_score(self, doc):
        pos = []
        for expr in doc.mscores:
            if expr.top_in_doc:
                for loc in expr.candidate.locations:
                    if loc[0] == doc.doc_id: # all doc offsets for the identical formula are listed
                        pos.append((loc[1], expr.candidate.new_scores))
        return(pos)
    
    def get_text_pos(self,doc):
        pos = []
        for (term,tlist) in doc.tpos.items():
            pos.append((term,tlist))
        return(pos)
        
    def output_query(self, out_file, cntl, topk, query_time_ms):
        out_file.write("\n")
        out_file.write("QUERY\t" + self.name + "\t" + str(query_time_ms) + "\n")

        if len(self.sorted_docs) == 0:
            # no results? nothing can be output
            return

        """
        for mquery in self.mqueries:
            out_file.write("E\t" + mquery.expression + "\n")
        if self.tquery:
            for keyword in self.tquery.keywords:
                out_file.write("P\t" + keyword + "\n")
        """
        d = MathDocument(cntl)

        min_score = self.sorted_docs[len(self.sorted_docs) - 1].final_score
        if len(self.sorted_docs) < topk:
            print("Warning: Query produced less than " + str(topk) + " documents. Results will be repeated", flush=True)

        # force output topk results
        for idx in range(topk):
            doc = self.sorted_docs[idx % len(self.sorted_docs)]

            positions = self.get_math_pos_with_score(doc)
            try:
                exprids = list(map(lambda pos: (d.find_mathml_id(doc.doc_id, pos[0]), pos[1]) ,positions))
            except(IOError):  # cannot read ids
                exprids = positions
            #out_file.write("R\t" + str(doc.doc_name) + "\t" + str(doc.final_score) + "\t(at: " + str(exprids) + str(self.get_text_pos(doc))+ ")\n")
            row_elements = [str(idx + 1)]

            if idx < len(self.sorted_docs):
                # use original score
                doc_score = doc.final_score
            else:
                doc_score = min_score

            if isinstance(doc_score, list):
                row_elements.append(str(doc_score[0]))
            else:
                row_elements.append(str(doc_score))

            row_elements.append(doc.doc_name)

            # add formulas *M*
            for exprid, mscore in exprids:
                row_elements += ["*M*", str(exprid), str(mscore[0])]

            # add Keywords *W*
            if self.tquery:
                for keyword in self.tquery.keywords:
                    row_elements += ["*W*", keyword, str(doc.tscore[1])]

            out_file.write("\t".join(row_elements) + "\n")

