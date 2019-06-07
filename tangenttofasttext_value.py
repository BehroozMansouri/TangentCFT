import os


def get_slt_elements(tuple, ignore_frp=True):
    """
    This method takes an slt tuple that was produced by tangent-s and returns back its elements (s1,s2,edge,frp)
    If the ignore_frp is set false it return all the four elements otherwise returns the first three elements
    :param tuple: the tangent-s tuple
    :param ignore_frp: if true would just return the first three elements that are the two nodes and their relationship
    :return: return the tuple elements
    """
    if ignore_frp:
        return tuple.split('\t')[:3]
    return tuple.split('\t')[:4]


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


def convert_node_elements(node_value, node_char_map, node_char_id, tokenize_all=False, tokenize_number=False):
    """
    This method takes in node values from tangent-s (first and second elements) and convert that to fasttext values
    two parameters decides how tokenization are done, we have three modes, node type and node values are always
    separated but values of the node can be also separated. For instance "N!123" can be tokenized as "N!" "1" "2" "3"
    we can do it in two modes: only the numbers being separated  and one all the values are separated
    :param node_value: node value (N!123 or V!a)
    :param node_char_map: the map that keep the tokenized item from tangent-s and the assigned char value
    :param node_char_id: the last id that is assigned to a tokenized item
    :param tokenize_all: if set true all the nodes such as Numbers N! and Variable V! will have tokenized values
    :param tokenize_number: if the tokenize_all is false and this param true, then only node values with type number
    will be tokenized
    :return: return the converted value along with the last assigned id to token (of first or second elements)
    """
    lst = []
    if "!" in node_value:
        if node_value == "O!":
            lst.append(node_value)
        else:
            parts = node_value.split("!")
            node_value = parts[1]
            lst.append(node_value)
    else:
        lst.append(node_value)
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


def tangent_to_fasttext(tangent_tuple_filepath, fasttext_tuple_filepath, ignore_frp=True, tokenize_all=False,
                        tokenize_number=False):

    # each slt element is given unique Id so that we can convert them back in embeddings
    node_ids = 70000
    path_ids = 60000

    node_map = {}
    path_map = {}

    for directory in os.listdir(tangent_tuple_filepath):
        if not os.path.exists(fasttext_tuple_filepath+"/"+directory):
            os.makedirs(fasttext_tuple_filepath+"/"+directory)
        for filename in os.listdir(tangent_tuple_filepath + "/" + directory):
            destination_file = open(fasttext_tuple_filepath + "/" + directory + "/" + filename, "w+")
            source_file = open(tangent_tuple_filepath + "/" + directory + "/" + filename)
            line = source_file.readline()
            line = line.rstrip("\n")
            while line:
                slt_tuple = ""
                slt_elements = get_slt_elements(line, ignore_frp=ignore_frp)

                converted_value, node_ids = convert_node_elements(slt_elements[0], node_map, node_ids,
                                                                  tokenize_all=tokenize_all,
                                                                  tokenize_number=tokenize_number)
                slt_tuple = slt_tuple + converted_value
                converted_value, node_ids = convert_node_elements(slt_elements[1], node_map, node_ids,
                                                                  tokenize_all=tokenize_all,
                                                                  tokenize_number=tokenize_number)
                slt_tuple = slt_tuple + converted_value

                converted_value, path_ids = convert_path_elements(slt_elements[2], path_map, path_ids)
                slt_tuple = slt_tuple + converted_value

                if len(slt_elements) == 4:
                    converted_value, path_ids = convert_path_elements(slt_elements[3], path_map, path_ids)
                    slt_tuple = slt_tuple + converted_value

                destination_file.write(slt_tuple + "\n")

                line = source_file.readline().rstrip("\n")
            source_file.close()
            destination_file.close()


def main():

    source = '/home/bm3302/FastText/OPTTuples_W2/'
    destination = '/home/bm3302/FastText/ft_opt_2/'
    tangent_to_fasttext(source, destination, ignore_frp=True)


if __name__ == "__main__":
    main()
