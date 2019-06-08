import sys
from sys import argv
from tangent_cft_module_formula import tangent_cft_module_formula
from tangent_cft_module_tuple import tangent_cft_module_tuple


def main(argv):

    if len(sys.argv) != 4:
        print("There should be 4 input: the first two are configuration file ids, the third is the embedding type 1 for"
              "tuple, 2 for formula. The last argument shows whether to save the vectors or not.")
        sys.exit(1)
    id_1 = int(argv[1])
    id_2 = int(argv[2])
    embedding_type = int(argv[3])
    save_id = bool(argv[4])
    for config_id in range(id_1, id_2+1):
        if embedding_type == 1:
            model = tangent_cft_module_tuple("/config/config_" + str(config_id) + ".csv")
        else:
            model = tangent_cft_module_formula("/config/config_" + str(config_id) + ".csv")
        model.run(config_id, save_id)


if __name__ == "__main__":
    main(argv)
