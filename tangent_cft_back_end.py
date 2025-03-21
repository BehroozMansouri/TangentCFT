import os

from Configuration.configuration import Configuration
from DataReader.mse_data_reader import MSEDataReader
from DataReader.wiki_data_reader import WikiDataReader
from Embedding_Preprocessing.encoder_tuple_level import TupleEncoder, TupleTokenizationMode

from tangent_cft_module import TangentCFTModule


class TangentCFTBackEnd:
    def __init__(self, config_file, path_data_set, is_wiki=True, read_slt=True, queries_directory_path=None):
        if is_wiki:
            self.data_reader = WikiDataReader(path_data_set, read_slt, queries_directory_path)
        else:
            self.data_reader = MSEDataReader(path_data_set, read_slt)
        self.config = Configuration(config_file)
        self.encoder_map_node = {}
        self.encoder_map_edge = {}
        self.node_id = 60000
        self.edge_id = 500
        self.module = None

    def train_model(self, map_file_path, model_file_path=None,
                    embedding_type=TupleTokenizationMode.Both_Separated, ignore_full_relative_path=True,
                    tokenize_all=False, tokenize_number=True):
        """
        This method is for training the tangent-cft model and saves the encoder and model after training is done.
        """
        self.module = TangentCFTModule()
        if os.path.isfile(map_file_path):
            self.__load_encoder_map(map_file_path)
        dictionary_formula_tuples_collection = self.__encode_train_tuples(embedding_type, ignore_full_relative_path,
                                                                          tokenize_all, tokenize_number)
        self.__save_encoder_map(map_file_path)
        print("training the fast text model...")
        self.module.train_model(self.config, list(dictionary_formula_tuples_collection.values()))

        if model_file_path is not None:
            print("saving the fast text model...")
            self.module.save_model(model_file_path)
        return dictionary_formula_tuples_collection

    def load_model(self, map_file_path, model_file_path,
                   embedding_type=TupleTokenizationMode.Both_Separated, ignore_full_relative_path=True,
                   tokenize_all=False,
                   tokenize_number=True
                   ):
        """Loads tangent-cft models and encoder map. While encoding the dataset, as new characters can be visited,
         the encoder map is saved again"""
        self.module = TangentCFTModule(model_file_path)
        self.__load_encoder_map(map_file_path)
        dictionary_formula_tuples_collection = self.__encode_train_tuples(embedding_type, ignore_full_relative_path,
                                                                          tokenize_all, tokenize_number)
        self.__save_encoder_map(map_file_path)
        return dictionary_formula_tuples_collection

    def retrieval(self, dictionary_formula_tuples_collection, embedding_type, ignore_full_relative_path, tokenize_all,
                  tokenize_number):
        """
        This method is used for retrieval, using one single representation such as SLT or OPT.
        """
        "indexing the collection and getting their vector values"
        tensor_values, index_formula_id = self.module.index_collection_to_tensors(dictionary_formula_tuples_collection)
        "reading queries tuples"
        dictionary_query_tuples = self.data_reader.get_query()
        retrieval_result = {}
        # print(len(retrieval_result))
        for query in dictionary_query_tuples:
            encoded_tuple_query = self.__encode_lst_tuples(dictionary_query_tuples[query], embedding_type,
                                                           ignore_full_relative_path, tokenize_all, tokenize_number)
            query_vec = self.module.get_query_vector(encoded_tuple_query)
            retrieval_result[query] = self.module.formula_retrieval(tensor_values, index_formula_id, query_vec)
        # print(len(retrieval_result))
        return retrieval_result

    def get_collection_query_vectors(self, dictionary_formula_tuples_collection, embedding_type, ignore_full_relative_path, tokenize_all,
                                     tokenize_number):
        """
        This method returns vector representations for formulae in collection and formula queries. The vectors are
        in numpy array and are returned in dictionary of formula id as key and vector as value.
        """
        index_formula_id = self.module.index_collection_to_numpy(dictionary_formula_tuples_collection)
        dictionary_query_tuples = self.data_reader.get_query()
        query_vectors = {}
        for query in dictionary_query_tuples:
            encoded_tuple_query = self.__encode_lst_tuples(dictionary_query_tuples[query], embedding_type,
                                                           ignore_full_relative_path, tokenize_all, tokenize_number)
            query_vec = self.module.get_query_vector(encoded_tuple_query)
            query_vectors[query] = query_vec
        return index_formula_id, query_vectors

    @staticmethod
    def create_result_file(result_query_doc, result_file_path, run_id):
        """
        Creates result files in Trec format that can be used for trec_eval tool
        """
        file = open(result_file_path, "w")
        for query_id in result_query_doc:
            count = 1
            query = "NTCIR12-MathWiki-" + str(query_id)
            line = query + " xxx "
            for x in result_query_doc[query_id]:
                doc_id = x
                score = result_query_doc[query_id][x]
                temp = line + doc_id + " " + str(count) + " " + str(score) + " Run_" + str(run_id)
                count += 1
                file.write(temp + "\n")
        file.close()

    def __encode_train_tuples(self, embedding_type, ignore_full_relative_path, tokenize_all, tokenize_number):
        """
        This methods read the collection queries in the dictionary of formula_id: tuple list and encodes the tuples according the criteria
        defined in the method inputs.
        The return value is dictionary of formula_id and list of encoded tuples
        """
        dictionary_lst_encoded_tuples = {}
        print("reading train data...")
        dictionary_formula_slt_tuple = self.data_reader.get_collection()
        print(len(dictionary_formula_slt_tuple.keys()))
        print("encoding train data...")
        for formula in dictionary_formula_slt_tuple:
            dictionary_lst_encoded_tuples[formula] = self.__encode_lst_tuples(dictionary_formula_slt_tuple[formula],
                                                                              embedding_type, ignore_full_relative_path,
                                                                              tokenize_all,
                                                                              tokenize_number)
        return dictionary_lst_encoded_tuples

    def __encode_lst_tuples(self, list_of_tuples, embedding_type, ignore_full_relative_path, tokenize_all,
                            tokenize_number):
        """
        This methods takes list of tuples and encode them and return encoded tuples
        """
        encoded_tuples, update_map_node, update_map_edge, node_id, edge_id = \
            TupleEncoder.encode_tuples(self.encoder_map_node, self.encoder_map_edge, self.node_id, self.edge_id,
                                       list_of_tuples, embedding_type, ignore_full_relative_path, tokenize_all,
                                       tokenize_number)

        self.node_id = node_id
        self.edge_id = edge_id
        self.encoder_map_node.update(update_map_node)
        self.encoder_map_edge.update(update_map_edge)
        return encoded_tuples

    def __save_encoder_map(self, map_file_path):
        """
        This method saves the encoder used for tokenization of formula tuples.
        map_file_path: file path to save teh encoder map in form of TSV file with column E/N \t character \t encoded value
        where E/N shows if the character is edge or node value, the character is tuple character to be encoded and encoded
        value is the value the encoder gave to character.
        """
        file = open(map_file_path, "w")
        for item in self.encoder_map_node:
            file.write("N" + "\t" + str(item) + "\t" + str(self.encoder_map_node[item]) + "\n")
        for item in self.encoder_map_edge:
            file.write("E" + "\t" + str(item) + "\t" + str(self.encoder_map_edge[item]) + "\n")
        file.close()

    def __load_encoder_map(self, map_file_path):
        """
        This method loads the saved encoder values into two dictionary used for edge and node values.
        """
        file = open(map_file_path)
        line = file.readline().strip("\n")
        while line:
            parts = line.split("\t")
            encoder_type = parts[0]
            symbol = parts[1]
            value = int(parts[2])
            if encoder_type == "N":
                self.encoder_map_node[symbol] = value
            else:
                self.encoder_map_edge[symbol] = value
            line = file.readline().strip("\n")
        "The id shows the id that should be assigned to the next character to be encoded (a character that is not seen)" \
        "Therefore there is a plus one in the following lines"
        self.node_id = max(list(self.encoder_map_node.values())) + 1
        self.edge_id = max(list(self.encoder_map_edge.values())) + 1
        file.close()
