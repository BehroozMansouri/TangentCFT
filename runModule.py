from sys import argv
from trainmodel import tangent_cft


def main(argv):

    id_1 = int(argv[1])
    id_2 = int(argv[2])

    for config_id in range(id_1, id_2+1):
        model = tangent_cft("/config/" + str(config_id) + ".txt")
        model.run(config_id, False)


if __name__ == "__main__":
    main(argv)
