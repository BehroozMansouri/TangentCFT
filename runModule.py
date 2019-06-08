from sys import argv
import tangent_cft_module


def main(argv):

    id_1 = int(argv[1])
    id_2 = int(argv[2])

    for config_id in range(id_1, id_2+1):
        model = tangent_cft_module("/config/config_" + str(config_id) + ".csv")
        model.run(config_id, False)


if __name__ == "__main__":
    main(argv)
