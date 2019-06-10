import datetime
import os
import numpy
from configuration import configuration
from tangent_cft_model import tangent_cft_model
from torch.autograd import Variable
import torch
import torch.nn.functional as F

os.environ['CUDA_VISIBLE_DEVICES'] = '0'
use_cuda = torch.cuda.is_available()
number_of_queries = 20


class tangent_cft_module:
    def __init__(self, config_file_path):
        """
            Take the configuration file path, this file define where the tangent_fasttext formulas are (those
            tangent-tuple encoded as char to be fed to fasttext). Both queries and collection dataset are in the same
            location. Also the destination where the queries vectors and all the other wikipedia formula vectors should
            be saved is defined in this file.
            Finally this file has the hyper_parameter setting for fasttext.
        """
        print("Setting Configuration")
        self.configuration = configuration(config_file_path)

        print("Reading train data")
        self.fast_text_train_data, self.collection_formula_map = self.read_training_data()
        self.query_formula_map = self.read_query_data()
        self.model = tangent_cft_model(self.configuration, self.fast_text_train_data)

    def run(self, run_id, save_vectors):
        """
            This is the main method that run the whole program, first the fasttext model is trained then the vectors for
            wikipedia formulas are saved, then the vectors for each of the queries are saved and another program will use
            these values.
        """
        print("Model is training.")
        train_time = self.model.train()
        print("train time\t" + str(train_time))

        print("Vectors are being created.")
        self.create_result_directories(save_vectors)
        doc_id_map, doc_tensors = self.get_collection_formula_vector(save_vectors)
        query_vector_map = self.save_query_formulas_vectors(save_vectors)

        sum = .0
        counter = 0
        f = open("Retrieval_Results/res_" + str(self.configuration.id), 'w')
        for queryId in query_vector_map:
            query_vec = query_vector_map[queryId]
            t1 = datetime.datetime.now()
            dist = F.cosine_similarity(doc_tensors, query_vec)
            index_sorted = torch.sort(dist, descending=True)[1]
            top_1000 = index_sorted[:1000]
            t2 = datetime.datetime.now()
            top_1000 = top_1000.data.cpu().numpy()
            sum += (t2 - t1).total_seconds() * 1000.0
            counter += 1
            cos_values = torch.sort(dist, descending=True)[0][:1000].data.cpu().numpy()
            count = 1
            query = "NTCIR12-MathWiki-" + str(queryId)
            line = query + " xxx "
            for x in top_1000:
                doc_id = doc_id_map[x]
                score = cos_values[count - 1]
                temp = line + doc_id + " " + str(count) + " " + str(score) + " Run_" + str(run_id)
                f.write(temp + "\n")
                count += 1
        f.close()
        print("Average retrieval time:")
        print(sum / counter)

    def get_collection_formula_vector(self, save_vectors):
        """
            This method for through each of the 17 Wikipedia directories, go through them file by file.
            Each file is a formula in Wikipedia dataset and for each of them we are creating a vector representation.
            To do so, for each of the SLT tuple in the formula we get its vector and the vector for formula is the average
            of its tuples vectors. This vector is saved in a file.
        """
        result = {}
        numpy_lst = []
        idx = 0
        for formula_id in self.collection_formula_map:
            try:
                formula_vector = self.get_vector_representation(self.collection_formula_map[formula_id])
                numpy_lst.append(formula_vector)
                result[idx] = formula_id
                idx += 1
            except:
                pass

            if save_vectors:
                numpy.savetxt(self.configuration.result_vector_file_path + "/" + str(formula_id),
                              formula_vector, newline=" ")

        temp = numpy.concatenate(numpy_lst, axis=0)
        tensor_values = Variable(torch.tensor(temp).double()).cuda()
        return result, tensor_values

    def save_query_formulas_vectors(self, save_vectors):
        """
        This method saves the vector representation of formula queries.
        We have 40 queries in the dataset of which the second 20 are wildcard queries.
        """
        query_vectors = {}
        for i in range(1, number_of_queries + 1):
            query_vector = self.get_vector_representation(self.query_formula_map[i])
            query_vectors[i] = Variable(torch.tensor(query_vector).double()).cuda()

            if save_vectors:
                numpy.savetxt(self.configuration.result_vector_file_path + "/Queries/" + str(i) + ".txt", query_vector,
                              newline=" ")
        return query_vectors

    def create_result_directories(self, save_vectors):
        """
            This method create the directories that results will be saved on
        """
        if not save_vectors:
            return

        os.makedirs(self.configuration.result_vector_file_path)
        for i in range(1, 17):
            os.makedirs(self.configuration.result_vector_file_path + "/" + str(i))
        os.makedirs(self.configuration.result_vector_file_path + "/" + "Queries")

    def read_training_data(self):
        pass

    def read_query_data(self):
        pass

    def get_vector_representation(self, formula_fast_text_representation):
        pass
