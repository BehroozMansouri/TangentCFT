
__author__ = 'FWTompa'


class TQuery:
    """
    TQuery(name,docs,keywords) where
        name is a string identifying the query
        docs is a dict mapping doc_id to (doc_name,score) pairs
        keywords is a sequence of search keywords and phrases
    """

    def __init__(self, name):
        self.name = name
        self.results = {}
        self.keywords = []

    def add_result(self, doc_id, doc_name, score, pos):
        self.results[doc_id] = (doc_name,score, pos)

    def add_keyword(self, keyword):
        self.keywords.append(keyword)

