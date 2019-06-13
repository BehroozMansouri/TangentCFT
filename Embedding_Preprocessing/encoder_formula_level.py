import os


def get_slt_elements(tuple, ignore_frp=True):
    if ignore_frp:
        result = tuple.split('\t')[:3]
    else:
        result = tuple.split('\t')[:4]
    return ",".join(result)


def tangent_to_fasttext(tangent_tuple_filepath, result_file_path, ignore_frp=True):
    # each slt element is given unique Id so that we can convert them back in embeddings
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
    source = '/home/bm3302/FastText/SLTTuples_W2/'
    destination = '/home/bm3302/FastText/s2_map/'
    tangent_to_fasttext(source, destination, ignore_frp=True)


if __name__ == "__main__":
    main()
