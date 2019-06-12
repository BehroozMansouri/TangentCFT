import os
from boto.cloudfront import logging
from tangent_cft_module import tangent_cft_module

number_of_queries = 20


class tangent_cft_module_tuple(tangent_cft_module):
    def __init__(self, config_file_path):
        tangent_cft_module.__init__(config_file_path)

    def read_training_data(self):
        lst_for_train = {}
        formula_map = {}

        for directory in os.listdir(self.config.filepath_fasttext):
            "Wikipedia pages in our dataset are in folders 1 to 16, only directory for queries is named Queries"
            if directory != "Queries":
                path = self.config.filepath_fasttext + directory
                for filename in os.listdir(path):
                    file = open(path + "/" + filename)
                    line = file.readline()
                    lst = []
                    while line:
                        line = line.rstrip('\n').strip()
                        if line is not "":
                            lst.append(line)
                        line = file.readline()
                    file.close()
                    lst_for_train.append(lst)
                    formula_map[filename] = lst
        return lst_for_train, formula_map

    def get_vector_representation(self, formula_fast_text_representation):
        """
         This method take the converted-tuple formula file path (the file on which a list the converted tuples for
         formula is saved, then it get vector representation of each of the tuple. The formula vector is the average of its
         tuples vectors.
         :param file_path: the formula file path where the fasttext tuple of that formula exists
         :return: return the vector representation of formula based on model trained
         """
        temp_vector = None
        first = True
        counter = 0
        for tuple in formula_fast_text_representation:
            # if the tuple vector cannot be extracted due to unseen n-gram, then we pass over that tuple.
            try:
                if first:
                    temp_vector = self.model.get_vector(tuple)
                    first = False
                else:
                    temp_vector = temp_vector + self.model.get_vector(tuple)
                counter = counter + 1
            except Exception as e:
                logging.exception(e)
        return temp_vector / counter

    def read_query_data(self):
        formula_map = {}
        for filename in os.listdir(self.config.filepath_fasttext+"Queries"):
            file = open(filename)
            line = file.readline()
            lst = []
            while line:
                line = line.rstrip('\n').strip()
                if line is not "":
                    lst.append(line)
                line = file.readline()
            file.close()
            formula_map[filename] = lst
        return formula_map
