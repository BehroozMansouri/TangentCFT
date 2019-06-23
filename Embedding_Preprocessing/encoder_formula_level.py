import os
import argparse
from Tools.Arg_Parse_Tools import readable_directory


def get_slt_elements(tuple, ignore_frp=True):
    if ignore_frp:
        result = tuple.split('\t')[:3]
    else:
        result = tuple.split('\t')[:4]
    return ",".join(result)


def tangent_to_fasttext(tangent_tuple_filepath, result_file_path, ignore_frp=True):
    slt_ids = 60000
    slt_map = {}
    encoded_file_Collection = open(result_file_path + "Collection", "w+")
    encoded_file_Queries = open(result_file_path + "Queries", "w+")
    for directory in os.listdir(tangent_tuple_filepath):
        if directory != "Queries":
            destination_file = encoded_file_Collection
        else:
            destination_file = encoded_file_Queries
        for filename in os.listdir(tangent_tuple_filepath + "/" + directory):

            source_file = open(tangent_tuple_filepath + "/" + directory + "/" + filename)
            formula = ""

            line = source_file.readline()
            line = line.rstrip("\n")
            while line:
                tuple = get_slt_elements(line, ignore_frp=ignore_frp)
                if tuple in slt_map.keys():
                    formula += slt_map[tuple]
                else:
                    val = chr(slt_ids)
                    slt_ids += 1
                    slt_map[tuple] = val
                    formula += val
                line = source_file.readline().rstrip("\n")
            filename = filename[:-4]
            destination_file.write(filename + "#~#" + formula + "\n")
            source_file.close()
    encoded_file_Collection.close()
    encoded_file_Queries.close()


def main():
    parser = argparse.ArgumentParser(description='Encodes Tangent Tuples to FastText Input. Each tuple is a word for '
                                                 'fastText model with its tokenized elements as its characters. \n'
                                                 'Example:\n Tuple:(V!X, N!12, n) --> Tokens(characters): V!,X,N!,12,n')

    parser.add_argument('-sd', metavar='source_directory', type=str, action=readable_directory,
                        help='String, directory path of tangent formula tuples. (Each formula is in a file with its '
                             'tuples in each line)', required=True)

    parser.add_argument('-dd', metavar='destination_directory', type=str, action=readable_directory,
                        help='String, directory path to save the encoded tangent formula tuples', required=True)

    parser.add_argument("--frp", help="Use full relative path. (See tangent-S paper)", type=bool, default=False)

    args = vars(parser.parse_args())
    source_directory = args['sd']
    destination_directory = args['dd']
    frp = args['frp']
    tangent_to_fasttext(source_directory, destination_directory, ignore_full_relative_path=frp)


if __name__ == "__main__":
    main()
