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
    destination_file = open(result_file_path, "w+")
    for directory in os.listdir(tangent_tuple_filepath):
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
            filename = directory + "\\" + filename
            destination_file.write(filename + "#~#" + formula + "\n")
            source_file.close()
    destination_file.close()


def main():
    source = '/home/bm3302/FastText/SLTTuples_W1/'
    destination = '/home/bm3302/FastText/formula_map_slt1.txt'
    tangent_to_fasttext(source, destination, ignore_frp=True)


if __name__ == "__main__":
    main()
