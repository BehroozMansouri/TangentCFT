import logging
import os
import numpy
from Configuration.configuration import Configuration
from tangent_cft_model import TangentCftModel
from torch.autograd import Variable
import torch
import torch.nn.functional as F

os.environ['CUDA_VISIBLE_DEVICES'] = '0'
use_cuda = torch.cuda.is_available()


class TangentCFTModule:
    def __init__(self, model_file_path=None):
        """
            Take the configuration file path, this file define where the tangent_fasttext formulas are (those
            tangent-tuple encoded as char to be fed to fasttext). Both queries and collection dataset are in the same
            location. Also the destination where the queries vectors and all the other wikipedia formula vectors should
            be saved is defined in this file.
            Finally this file has the hyper_parameter setting for fasttext.
        """
        self.model = TangentCftModel()
        if model_file_path is not None:
            print("Loading the model")
            self.model.load_model(model_file_path)

    def train_model(self, configuration, lst_lst_encoded_tuples):
        print("Setting Configuration")
        self.model.train(configuration, lst_lst_encoded_tuples)
        return self.model

    def save_model(self, model_file_path):
        self.model.save_model(model_file_path)

    def index_collection(self, dictionary_formula_lst_encoded_tuples):
        numpy_lst = []
        index_formula_id = {}
        idx = 0
        for formula in dictionary_formula_lst_encoded_tuples:
            numpy_lst.append(self.__get_vector_representation(dictionary_formula_lst_encoded_tuples[formula]))
            index_formula_id[idx] = formula
        temp = numpy.concatenate(numpy_lst, axis=0)
        tensor_values = Variable(torch.tensor(temp).double()).cuda()
        return tensor_values, index_formula_id

    def get_query_vector(self, lst_encoded_tuples):
        return self.__get_vector_representation(lst_encoded_tuples)

    @staticmethod
    def formula_retrieval(collection_tensor, formula_index, query_vector):
        query_vec = torch.from_numpy(query_vector)
        dist = F.cosine_similarity(collection_tensor, query_vec)
        index_sorted = torch.sort(dist, descending=True)[1]
        top_1000 = index_sorted[:1000]
        top_1000 = top_1000.data.cpu().numpy()
        cos_values = torch.sort(dist, descending=True)[0][:1000].data.cpu().numpy()
        result = {}
        count = 1
        for x in top_1000:
            doc_id = formula_index[x]
            score = cos_values[count - 1]
            result[doc_id] = score
            count += 1
        return result

    def __get_vector_representation(self, lst_encoded_tuples):
        """
         This method take the converted-tuple formula file path (the file on which a list the converted tuples for
         formula is saved, then it get vector representation of each of the tuple. The formula vector is the average of its
         tuples vectors.
        :param lst_encoded_tuples: averaging vector representation for these tuples
        :return: vector representation for the formula
        """
        temp_vector = None
        first = True
        counter = 0
        for encoded_tuple in lst_encoded_tuples:
            # if the tuple vector cannot be extracted due to unseen n-gram, then we pass over that tuple.
            try:
                if first:
                    temp_vector = self.model.get_vector_representation(encoded_tuple)
                    first = False
                else:
                    temp_vector = temp_vector + self.model.get_vector_representation(encoded_tuple)
                counter = counter + 1
            except Exception as e:
                logging.exception(e)
        return (temp_vector / counter).reshape(1, self.vector_size)
