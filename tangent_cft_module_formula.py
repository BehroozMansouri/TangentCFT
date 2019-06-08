import os
import torch
import tangent_cft_module

os.environ['CUDA_VISIBLE_DEVICES'] = '0'
use_cuda = torch.cuda.is_available()
number_of_queries = 20


class tangent_cft_module_formula(tangent_cft_module):
    def __init__(self, config_file_path):
        tangent_cft_module.__init__(config_file_path)

    "Each hierarchy that we consider for embedding (formula/tuple) needs it own reading file"
    def read_training_data(self):
        map_for_train = {}
        formula_map = {}
        "For the training we have a file called collection, where each formula and its encoded value exists there" \
        "each row is a formula#~#encoded_value"

        file = open(self.configuration.filepath_fasttext + "Collection")
        line = file.readline()
        while line:
            line = line.rstrip('\n').strip()
            formula = line.split("#~#")[1]
            page_formula_id = line.split("#~#")[0]
            formula_map[page_formula_id] = formula
            wiki_page = page_formula_id.split(":")[0]
            formula_id = page_formula_id.split(":")[1]

            if wiki_page in map_for_train.keys():
                map_for_train[wiki_page][formula_id] = formula
            else:
                map = {formula_id: formula}
                map_for_train[wiki_page] = map
            line = file.readline()
        file.close()

        list_for_train = []
        for key in map_for_train:
            map_temp = map_for_train[key]
            lst = []
            for id in sorted(map_temp):
                lst.append(map_temp[id])
            list_for_train.append(lst)

        return list_for_train, formula_map

    def get_vector_representation(self, formula_fast_text_representation):
        """
         This method take the converted-tuple formula file path (the file on which a list the converted tuples for
         formula is saved, then it get vector representation of each of the tuple. The formula vector is the average of its
         tuples vectors.
         :param formula_fast_text_representation:
         :return: return the vector representation of formula based on model trained
         """
        return self.model.get_vector(formula_fast_text_representation)

    def read_query_data(self):
        formula_map = {}
        for filename in os.listdir(self.config.filepath_fasttext + "Queries"):
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
