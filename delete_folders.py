import shutil


def main():
    for i in range(2065, 2300):
        value = "/home/bm3302/FastText/Run_Result_" + str(i)
        #print(value)
        shutil.rmtree(value)
        #print("deleted"+str(i))


if __name__ == '__main__':
    main()
