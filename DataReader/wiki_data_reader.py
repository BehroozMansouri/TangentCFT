import os
import unicodedata
from abc import ABC

from DataReader.abstract_data_reader import AbstractDataReader
from TangentS.math_tan.math_document import MathDocument
from TangentS.math_tan.math_extractor import MathExtractor


class WikiDataReader(AbstractDataReader, ABC):
    def __init__(self, collection_file_path, read_slt=True, queries_directory_path=None):
        self.read_slt = read_slt
        self.collection_file_path = collection_file_path
        self.queries_directory_path = queries_directory_path
        super()

    def get_collection(self, ):
        """
        This method read the NTCIR-12 formulae in the collection.
        To handle formulae with special characters line 39 normalizes the unicode data.
        The return value is a dictionary of formula id (as key) and list of tuples (as value)
        """
        except_count = 0
        dictionary_formula_tuples = {}
        root = self.collection_file_path
        for directory in os.listdir(root):
            temp_address = root + "/" + directory + "/"
            if not os.path.isdir(temp_address):
                continue
            
            for filename in os.listdir(temp_address):
                file_path = temp_address + filename
                parts = filename.split('/')
                file_name = os.path.splitext(parts[len(parts) - 1])[0]
                try:
                    (ext, content) = MathDocument.read_doc_file(file_path)
                    formulas = MathExtractor.parse_from_xml(content, 1, operator=(not self.read_slt), missing_tags=None,
                                                            problem_files=None)
                    temp = str(unicodedata.normalize('NFKD', file_name).encode('ascii', 'ignore'))
                    temp = temp[2:]
                    file_name = temp[:-1]
                    for key in formulas:
                        tuples = formulas[key].get_pairs(window=2, eob=True)
                        dictionary_formula_tuples[file_name + ":" + str(key)] = tuples
                except:
                    except_count += 1
                    print(file_name)
        return dictionary_formula_tuples

    def get_query(self, ):
        """
        This method reads the NTCIR-12 the queries.
        Note that the Tangent-CFT does not support queries with Wildcard,
        Therefore the query range is 1 to 20 which are concerete queries in NTCIR-12.
        """
        except_count = 0
        dictionary_query_tuples = {}
        for j in range(1, 21):
            temp_address = self.queries_directory_path + '/' + str(j) + '.html'
            try:
                (ext, content) = MathDocument.read_doc_file(temp_address)
                formulas = MathExtractor.parse_from_xml(content, 1, operator=(not self.read_slt), missing_tags=None,
                                                        problem_files=None)
                for key in formulas:
                    tuples = formulas[key].get_pairs(window=2, eob=True)
                    dictionary_query_tuples[j] = tuples
            except:
                except_count += 1
                print(j)
        return dictionary_query_tuples
