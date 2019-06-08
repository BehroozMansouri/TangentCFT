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


class tangent_cft:
    def __init__(self, config_file_path):
        """
            Take the configuration file path, this file define where the tangent_fasttext formulas are (those
            tangent-tuple encoded as char to be fed to fasttext). Both queries and collection dataset are in the same
            location. Also the destination where the queries vectors and all the other wikipedia formula vectors should
            be saved is defined in this file.
            Finally this file has the hyper_parameter setting for fasttext.
        """
        self.configuration = configuration(config_file_path)
        self.model = tangent_cft_model(self.configuration)
        print("model configuration is set")

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
        doc_id_map, doc_tensors = self.save_Wikipedia_formulas_vectors(save_vectors)
        query_vector_map = self.save_query_formulas_vectors(save_vectors)

        sum = .0
        counter = 0
        f = open("/Retrieval_Results/res_"+str(self.configuration.id), 'w')
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

    def save_Wikipedia_formulas_vectors(self, save_vectors):
        """
            This method for through each of the 17 Wikipedia directories, go through them file by file.
            Each file is a formula in Wikipedia dataset and for each of them we are creating a vector representation.
            To do so, for each of the SLT tuple in the formula we get its vector and the vector for formula is the average
            of its tuples vectors. This vector is saved in a file.
        """
        result = {}
        numpy_lst = []
        idx = 0

        for i in range(1, 17):
            file_path = self.configuration.file_path_fasttext + str(i)
            for filename in os.listdir(file_path):
                formula_vector = self.get_formula_vector(file_path + "/" + filename)
                numpy_lst.append(formula_vector)
                result[idx] = filename
                idx += 1

                if save_vectors:
                    numpy.savetxt(self.configuration.result_vector_file_path + "/" + str(i) + "/" + filename,
                                  formula_vector, newline=" ")

        temp = numpy.concatenate(numpy_lst, axis=0)
        tensor_values = Variable(torch.tensor(temp).double()).cuda()
        return result, tensor_values

    def get_formula_vector(self, file_path):
        """
        This method take the converted-tuple formula file path (the file on which a list the converted tuples for
        formula is saved, then it get vector representation of each of the tuple. The formula vector is the average of its
        tuples vectors.
        :param file_path: the formula file path where the fasttext tuple of that formula exists
        :return: return the vector representation of formula based on model trained
        """
        sourcefile = open(file_path)

        # read each slt for a formula and convert its element to char
        line = sourcefile.readline()
        temp_vector = None
        first = True
        counter = 0
        while line:
            line = line.rstrip('\n').strip()
            # if the tuple vector cannot be extracted due to unseen n-gram, then we pass over that tuple.
            try:
                if first:
                    temp_vector = self.model.get_vector(line)
                    first = False
                else:
                    temp_vector = temp_vector + self.model.get_vector(line)
                counter = counter + 1
            except:
                print(file_path)
                pass
            line = sourcefile.readline()
        sourcefile.close()
        return temp_vector / counter

    def save_query_formulas_vectors(self, save_vectors):
        """
        This method saves the vector representation of formula queries.
        We have 40 queries in the dataset of which the second 20 are wildcard queries.
        """
        query_vectors = {}
        file_path_query = self.configuration.file_path_fasttext + "Queries/"
        for i in range(1, number_of_queries+1):
            query_vector = self.get_formula_vector(file_path_query + str(i) + ".txt")
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
