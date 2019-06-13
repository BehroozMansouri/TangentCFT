import os
from enum import Enum
import argparse
from sys import argv


def required_length(min_value, max_value):
    class RequiredLength(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if not min_value <= (values) <= max_value:
                msg = 'argument "{f}" requires between {min_value} and {max_value} arguments'.format(
                    f=self.dest, min_value=min_value, max_value=max_value)
                raise argparse.ArgumentTypeError(msg)
            setattr(args, self.dest, values)
    return RequiredLength


class readable_directory(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir=values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("readable_dir: {0} is not a valid path.".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            raise argparse.ArgumentTypeError("readable_dir: {0} is not a readable dir.".format(prospective_dir))


class Node_token(Enum):
    """
    This enum shows how the tokenization of nodes should be done, given the node N!1234 for each of the enum values
    the outputs are:
    Value : 1234
    Type:   N!
    Both_Separated: N!, 1234
    Both_Non_Separated: N!1234
    """
    Value = 1
    Type = 2
    Both_Separated = 3
    Both_Non_Separated = 4


def get_slt_elements(tangent_tuple, ignore_full_relative_path=True):
    """
    This method takes an slt tuple that was produced by tangent-s and returns back its elements (s1,s2,edge,frp)
    If the ignore_frp is set false it return all the four elements otherwise returns the first three elements
    :param tangent_tuple: the tangent-s tuple
    :param ignore_full_relative_path: if true would just return the first three elements that are the two nodes and their relationship
    :return: return the tuple elements
    """
    if ignore_full_relative_path:
        return tangent_tuple.split('\t')[:3]
    return tangent_tuple.split('\t')[:4]


def get_char_value(lst, node_char_map, node_char_id):
    """
    This method handles the char assigning process, taken a list of tokens to assign char value to them, this assigning
    is done by the map
    node_char_id show the id that can be given at the moment to the unseen tokens
    :param lst: list of token that are going to be converted to char values
    :param node_char_map: map that will be used for previously seen token to which a char is assigned
    :param node_char_id: id that will be used for new unseen tokens
    :return: return the converted values along with the new id (in the case it is updated from assigning new char to an
     unseen token
    """
    converted_value = ""
    for item in lst:
        if item in node_char_map:
            value = node_char_map.get(item)
        else:
            node_char_map[item] = chr(node_char_id)
            value = chr(node_char_id)
            node_char_id = node_char_id + 1
        converted_value += value
    return converted_value, node_char_id


def convert_node_elements(node, node_char_map, node_char_id, embedding_type, tokenize_all=False, tokenize_number=False):
    """
    This method takes in node values from tangent-s (first and second elements) and convert that to fasttext values
    two parameters decides how tokenization are done, we have three modes, node type and node values are always
    separated but values of the node can be also separated. For instance "N!123" can be tokenized as "N!" "1" "2" "3"
    we can do it in two modes: only the numbers being separated  and one all the values are separated
    :param embedding_type: decided how the tokenization should be done
    :param node: node value (N!123 or V!a)
    :param node_char_map: the map that keep the tokenized item from tangent-s and the assigned char value
    :param node_char_id: the last id that is assigned to a tokenized item
    :param tokenize_all: if set true all the nodes such as Numbers N! and Variable V! will have tokenized values
    :param tokenize_number: if the tokenize_all is false and this param true, then only node values with type number
    will be tokenized
    :return: return the converted value along with the last assigned id to token (of first or second elements)
    """
    lst = []
    if "!" in node:
        if node == "O!":
            lst.append(node)
        else:
            node_type = node.split("!")[0]
            node_value = node.split("!")[1]

            if embedding_type == Node_token.Type:
                lst.append(node_type)
            elif embedding_type == Node_token.Value:
                if not tokenize_all and (not tokenize_number or node_type != "N!"):
                    lst.append(node_value)
                else:
                    for val in node_value:
                        lst.append(val)
            elif embedding_type == Node_token.Both_Separated:
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
    return get_char_value(lst, node_char_map, node_char_id)


def convert_path_elements(path, edge_char_map, edge_char_id):
    """
    This method handles conversion of third and fourth elements that are related to edges in slt showing the path from
    the first and second node, along with the full relative path from node to root (fourth element)
    :param path: path to be encoded which is set of edge labels
    :param edge_char_map: map containing the edge lable and the assigned value
    :param edge_char_id: the last id assigned to a edge label
    :return: converted value of encoded path and the last id assigned to label
    """
    converted_value = ""
    for label in path:
        if label in edge_char_map:
            value = edge_char_map.get(label)
        else:
            edge_char_map[label] = chr(edge_char_id)
            value = chr(edge_char_id)
            edge_char_id = edge_char_id + 1
        converted_value += value
    return converted_value, edge_char_id


def tangent_to_fasttext(tangent_tuple_file_path, fasttext_tuple_file_path, ignore_full_relative_path=True,
                        tokenize_all=False, tokenize_number=False, embedding_type=Node_token.Both_Separated):

    # each slt element is given unique Id so that we can convert them back in embeddings
    node_ids = 70000
    path_ids = 60000

    node_map = {}
    path_map = {}

    for directory in os.listdir(tangent_tuple_file_path):
        if not os.path.exists(fasttext_tuple_file_path + "/" + directory):
            os.makedirs(fasttext_tuple_file_path + "/" + directory)
        for filename in os.listdir(tangent_tuple_file_path + "/" + directory):
            destination_file = open(fasttext_tuple_file_path + "/" + directory + "/" + filename, "w+")
            source_file = open(tangent_tuple_file_path + "/" + directory + "/" + filename)
            line = source_file.readline()
            line = line.rstrip("\n")
            while line:
                slt_tuple = ""
                slt_elements = get_slt_elements(line, ignore_full_relative_path=ignore_full_relative_path)

                converted_value, node_ids = convert_node_elements(slt_elements[0], node_map, node_ids, embedding_type,
                                                                  tokenize_all=tokenize_all,
                                                                  tokenize_number=tokenize_number)
                slt_tuple = slt_tuple + converted_value
                converted_value, node_ids = convert_node_elements(slt_elements[1], node_map, node_ids, embedding_type,
                                                                  tokenize_all=tokenize_all,
                                                                  tokenize_number=tokenize_number)
                slt_tuple = slt_tuple + converted_value
                converted_value, path_ids = convert_path_elements(slt_elements[2], path_map, path_ids)
                slt_tuple = slt_tuple + converted_value

                "Encode the full relative path"
                if not ignore_full_relative_path:
                    converted_value, path_ids = convert_path_elements(slt_elements[3], path_map, path_ids)
                    slt_tuple = slt_tuple + converted_value

                destination_file.write(slt_tuple + "\n")

                line = source_file.readline().rstrip("\n")
            source_file.close()
            destination_file.close()


def main():
    parser = argparse.ArgumentParser(description='Encodes Tangent Tuples to FastText Input. Each tuple is a word for '
                                                 'fastText model with its tokenized elements as its characters. \n'
                                                 'Example:\n Tuple:(V!X, N!12, n) --> Tokens(characters): V!,X,N!,12,n')

    parser.add_argument('source_directory', metavar='source_directory', type=str, action=readable_directory,
                        help='String, directory path of tangent formula tuples. (Each formula is in a file with its '
                             'tuples in each line)')

    parser.add_argument('destination_directory', metavar='destination_directory', type=str, action=readable_directory,
                        help='String, directory path to save the encoded tangent formula tuples')

    parser.add_argument("--frp", help="Use full relative path. (See tangent-S paper)", type=bool, default=False)

    parser.add_argument("--tokenization", help="Tokenization type, 1:value, 2:type, 3:'type','value', 4:'type+value'",
                        action=required_length(1, 4), type=int, default=3)

    args = vars(parser.parse_args())

    source_directory = args['source_directory']
    destination_directory = args['destination_directory']
    frp = args['frp']
    tokenization = args['tokenization']

    tangent_to_fasttext(source_directory, destination_directory, ignore_full_relative_path=frp,
                        embedding_type=Node_token(tokenization))


if __name__ == "__main__":
    main(argv)
