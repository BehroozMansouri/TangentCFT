import os
import numpy
from config import config
from tangent_cft_model import tangent_cft_model


class tangent_cft:
    def __init__(self, config_file_path):
        """
            Take the configuration file path, this file define where the tangent_fasttext formulas are (those
            tangent-tuple encoded as char to be fed to fasttext). Both queries and corpus dataset are in the same
            location. Also the destination where the query vector and all the other wikipedia formula vectors are saved
            is defined in this file.
            Finally this file has the hyper_parameter setting for fasttext.
        """
        self.configuration = config(config_file_path)
        self.model = tangent_cft_model(self.configuration)
        print("model configuration is set")

    def run(self):
        """
            This is the main method that run the whole program, first the fasttext model is trained then the vectors for
            wikipedia formulas are saved, then the vectors for each of the queries are saved and another program will use
            these values.
        """
        print("Model is training.")
        self.model.train()
        self.create_result_directories()
        print("Vectors are being created.")
        self.save_Wikipedia_formulas_vectors()
        self.save_query_formulas_vectors()

    def save_Wikipedia_formulas_vectors(self):
        """
            This method for through each of the 17 Wikipedia directories, go through them file by file.
            Each file is a formula in Wikipedia dataset and for each of them we are creating a vector representation.
            To do so, for each of the SLT tuple in the formula we get its vector and the vector for formula is the average
            of its tuples vectors. This vector is saved in a file.
        """
        for i in range(1, 17):
            file_path = self.configuration.filepath_fasttext + str(i)
            for filename in os.listdir(file_path):
                formula_vec = self.get_formula_vector(file_path + "/" + filename)
                numpy.savetxt(self.configuration.result_file_path + "/"+str(i) + "/" + filename, formula_vec, newline=" ")

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

    def save_query_formulas_vectors(self):
        """
        This method saves the vector representation of formula queries.
        We have 40 queries in the dataset of which the second 20 are wildcard queries.
        """
        file_path_query = self.configuration.filepath_fasttext + "Queries/"
        for i in range(1, 70):
            print(i)
            query_vector = self.get_formula_vector(file_path_query + str(i) + ".txt")
            numpy.savetxt(self.configuration.result_file_path+"/Queries/" + str(i) + ".txt", query_vector, newline=" ")

    def create_result_directories(self):
        """
            This method create the directories that results will be saved on
        """
        os.makedirs(self.configuration.result_file_path)
        for i in range(1, 17):
            os.makedirs(self.configuration.result_file_path + "/" + str(i))
        os.makedirs(self.configuration.result_file_path + "/" + "Queries")