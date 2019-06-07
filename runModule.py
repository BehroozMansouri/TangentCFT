from sys import argv
from trainmodel import tangent_cft


def main(argv):

    i = int(argv[1])
    j = int(argv[2])

    for val in range(i, j+1):
        model = tangent_cft("/home/bm3302/FastText/config" + str(val) + ".txt")
        model.run()


if __name__ == "__main__":
    main(argv)