import os
from enum import Enum
import os.path


class TupleTokenizationMode(Enum):
    """
    This enum shows how the tokenization of nodes should be done, given the node N!1234 for each of the enum values
    the outputs are:
    Tokenization type , tokens
    Value : 1234
    Type:   N!
    Both_Separated: N!, 1234
    Both_Non_Separated: N!1234
    """
    Value = 1
    Type = 2
    Both_Separated = 3
    Both_Non_Separated = 4


class TupleEncoder:
    def __init__(self,):
        self.__encoder_map_node = {}
        self.__encoder_map_path = {}
        self.__create_path_map()
        self.update_list = {}
        self.node_id = None

    def __create_path_map(self):
        # Symbol_Layout_Tree edge labels
        self.__encoder_map_path["n"] = chr(500)
        self.__encoder_map_path["w"] = chr(501)
        self.__encoder_map_path["a"] = chr(502)
        self.__encoder_map_path["b"] = chr(503)
        self.__encoder_map_path["e"] = chr(504)
        self.__encoder_map_path["u"] = chr(505)
        self.__encoder_map_path["o"] = chr(506)
        self.__encoder_map_path["c"] = chr(507)
        self.__encoder_map_path["d"] = chr(508)
        # Operator_Tree edge labels
        self.__encoder_map_path["0"] = chr(509)
        self.__encoder_map_path["1"] = chr(510)
        self.__encoder_map_path["2"] = chr(511)
        self.__encoder_map_path["3"] = chr(512)
        self.__encoder_map_path["4"] = chr(513)
        self.__encoder_map_path["5"] = chr(514)
        self.__encoder_map_path["6"] = chr(515)
        self.__encoder_map_path["7"] = chr(516)
        self.__encoder_map_path["8"] = chr(517)
        self.__encoder_map_path["9"] = chr(518)

    def encode_tuples(self, node_map, node_id, math_tuples, embedding_type=TupleTokenizationMode.Both_Separated,
                      ignore_full_relative_path=True, tokenize_all=False, tokenize_number=True):
        """
        Takes the encoder map (which can be empty) and the last node id and enumerates the tuple tokens to converts the
        tuples to words (with n-gram as each tokenized tuple element) to make the formulas ready to be fed to fasttext
        :param node_map: dictionary of tokens and their id
        :param node_id: the last node id
        :param math_tuples: list of formula tuples (which are extracted by Tangent-S) to be encoded
        :param embedding_type: one of the four possible tokenization model
        :param ignore_full_relative_path: determines to ignore the full relative path or not (default True)
        :param tokenize_all: determines to tokenize all elements (such as numbers and text) (default False)
        :param tokenize_number: determines to tokenize the numbers or not (default True)
        :return:
        """
        self.node_id = node_id
        self.__encoder_map_node = node_map
        encoded_tuples = []
        for math_tuple in math_tuples:
            encoded_slt_tuple = ""
            slt_elements = self.__get_slt_elements(math_tuple, ignore_full_relative_path=ignore_full_relative_path)

            converted_value = self.__convert_node_elements(slt_elements[0], embedding_type,
                                                           tokenize_all=tokenize_all,
                                                           tokenize_number=tokenize_number)
            encoded_slt_tuple = encoded_slt_tuple + converted_value

            converted_value = self.__convert_node_elements(slt_elements[1], embedding_type,
                                                           tokenize_all=tokenize_all,
                                                           tokenize_number=tokenize_number)
            encoded_slt_tuple = encoded_slt_tuple + converted_value

            converted_value = self.__convert_path_elements(slt_elements[2])
            encoded_slt_tuple = encoded_slt_tuple + converted_value
            "Encode the full relative path"
            if not ignore_full_relative_path:
                converted_value = self.__convert_path_elements(slt_elements[3])
                encoded_slt_tuple = encoded_slt_tuple + converted_value
            encoded_tuples.append(encoded_slt_tuple)

        temp_update_list = self.update_list
        self.update_list = {}
        return encoded_tuples, temp_update_list, self.node_id

    def __convert_node_elements(self, node, embedding_type, tokenize_all=False, tokenize_number=False):
        lst = []
        if "!" in node:
            if node == "O!":
                lst.append(node)
            else:
                node_type = node.split("!")[0]+"!"
                node_value = node.split("!")[1]

                if embedding_type == TupleTokenizationMode.Type:
                    lst.append(node_type)
                elif embedding_type == TupleTokenizationMode.Value:
                    if not tokenize_all and (not tokenize_number or node_type != "N!"):
                        lst.append(node_value)
                    else:
                        for val in node_value:
                            lst.append(val)
                elif embedding_type == TupleTokenizationMode.Both_Separated:
                    lst.append(node_type)
                    if not tokenize_all and (not tokenize_number or node_type != "N!"):
                        lst.append(node_value)
                    else:
                        for val in node_value:
                            lst.append(val)
                else:
                    lst.append(node)
        else:
            lst.append(node)
        return self.__get_char_value(lst)

    def __convert_path_elements(self, path):
        converted_value = ""
        for label in path:
            value = self.__encoder_map_path.get(label)
            converted_value += value
        return converted_value

    def __get_char_value(self, lst):
        converted_value = ""
        for item in lst:
            if item in self.__encoder_map_node:
                value = chr(self.__encoder_map_node.get(item))
            else:
                value = chr(self.node_id)
                self.update_list[item] = self.node_id
                self.__encoder_map_node[item] = self.node_id
                self.node_id = self.node_id + 1
            converted_value += value
        return converted_value

    @staticmethod
    def __get_slt_elements(tangent_tuple, ignore_full_relative_path=True):
        if ignore_full_relative_path:
            return tangent_tuple.split('\t')[:3]
        return tangent_tuple.split('\t')[:4]
