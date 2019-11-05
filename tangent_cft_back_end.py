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
        self.tuple_encoder = TupleEncoder()
        self.encoder_map = {}
        self.node_id = 60000
        self.module = None

    def __encode_train_tuples(self, embedding_type, ignore_full_relative_path, tokenize_all, tokenize_number):
        dictionary_lst_encoded_tuples = {}
        print("reading train data...")
        dictionary_formula_slt_tuple = self.data_reader.get_collection()
        print("encoding train data...")
        for formula in dictionary_formula_slt_tuple:
            dictionary_lst_encoded_tuples[formula] = self.__encode_lst_tuples(dictionary_formula_slt_tuple[formula],
                                                                              embedding_type, ignore_full_relative_path,
                                                                              tokenize_all,
                                                                              tokenize_number)
        return dictionary_lst_encoded_tuples

    def __encode_lst_tuples(self, list_of_tuples, embedding_type, ignore_full_relative_path, tokenize_all,
                            tokenize_number):
        encoded_tuples, temp_update_list, node_id = self.tuple_encoder.encode_tuples(self.encoder_map, self.node_id,
                                                                                     list_of_tuples, embedding_type,
                                                                                     ignore_full_relative_path,
                                                                                     tokenize_all, tokenize_number)

        self.node_id = node_id
        self.encoder_map.update(temp_update_list)
        return encoded_tuples

    def __save_encoder_map(self, map_file_path):
        file = open(map_file_path, "w")
        for item in self.encoder_map:
            file.write(str(item) + "," + str(self.encoder_map[item]) + "\n")
        file.close()

    def __load_encoder_map(self, map_file_path):
        file = open(map_file_path)
        line = file.readline().strip("\n")
        while line:
            self.encoder_map[(line.split(",")[0])] = int(line.split(",")[1])
            line = file.readline().strip("\n")
        self.node_id = max(list(self.encoder_map.values())) + 1
        file.close()

    def train_model(self, map_file_path, model_file_path=None,
                    embedding_type=TupleTokenizationMode.Both_Separated, ignore_full_relative_path=True,
                    tokenize_all=False,
                    tokenize_number=True):
        self.module = TangentCFTModule()
        dictionary_formula_tuples_collection = self.__encode_train_tuples(embedding_type, ignore_full_relative_path,
                                                                          tokenize_all, tokenize_number)
        print("training the fast text model...")
        self.module.train_model(self.config, list(dictionary_formula_tuples_collection.values()))
        self.__save_encoder_map("Saved_model/" + map_file_path)
        if model_file_path is not None:
            print("saving the fast text model...")
            self.module.save_model(model_file_path)
        return dictionary_formula_tuples_collection

    def load_model(self, map_file_path, model_file_path,
                   embedding_type=TupleTokenizationMode.Both_Separated, ignore_full_relative_path=True,
                   tokenize_all=False,
                   tokenize_number=True
                   ):
        self.module = TangentCFTModule(model_file_path)
        self.__load_encoder_map(map_file_path)
        dictionary_formula_tuples_collection = self.__encode_train_tuples(embedding_type, ignore_full_relative_path,
                                                                          tokenize_all, tokenize_number)
        self.__save_encoder_map(map_file_path)
        return dictionary_formula_tuples_collection

    def retrieval(self, dictionary_formula_tuples_collection, embedding_type, ignore_full_relative_path, tokenize_all,
                  tokenize_number):
        tensor_values, index_formula_id = self.module.index_collection(dictionary_formula_tuples_collection)
        dictionary_query_tuples = self.data_reader.get_query()
        retrieval_result = {}
        for query in dictionary_query_tuples:
            encoded_tuple_query = self.__encode_lst_tuples(dictionary_query_tuples[query], embedding_type,
                                                           ignore_full_relative_path, tokenize_all, tokenize_number)
            query_vec = self.module.get_query_vector(encoded_tuple_query)
            retrieval_result[query] = self.module.formula_retrieval(tensor_values, index_formula_id, query_vec)
        return retrieval_result

    @staticmethod
    def create_result_file(result_query_doc, result_file_path, run_id):
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
