class configuration:

    def __init__(self):
        self.context_window_size = None
        self.file_path_fasttext = None
        self.hs = None
        self.id = None
        self.iter = None
        self.max = None
        self.min = None
        self.negative = None
        self.ngram = None
        self.result_vector_file_path = None
        self.skip_gram = None
        self.vector_size = None

    def __init__(self, config_file_path):
        file = open(config_file_path)
        self.context_window_size = int(file.readline().rstrip('\n').split(",")[1])
        self.file_path_fasttext = file.readline().rstrip('\n').split(",")[1]
        self.hs = int(file.readline().rstrip('\n').split(",")[1])
        self.id = int(file.readline().rstrip('\n').split(",")[1])
        self.iter = int(file.readline().rstrip('\n').split(",")[1])
        self.max = int(file.readline().rstrip('\n').split(",")[1])
        self.min = int(file.readline().rstrip('\n').split(",")[1])
        self.negative = int(file.readline().rstrip('\n').split(",")[1])
        self.ngram = int(file.readline().rstrip('\n').split(",")[1])
        self.result_vector_file_path = file.readline().rstrip('\n').split(",")[1]
        self.skip_gram = int(file.readline().rstrip('\n').split(",")[1])
        self.vector_size = int(file.readline().rstrip('\n').split(",")[1])
        file.close()

    def write_to_file(self, config_file_path):
        file = open(config_file_path, "w")
        attribute_map = self.__dict__
        for item in attribute_map:
            file.write(item +"," + str(attribute_map[item]) + "\n")
        # file.write("file_path_fasttext,"+self.file_path_fasttext+"\n")
        # file.write("result_vector_file_path,"+self.result_vector_file_path + "\n")
        # file.write("id,"+str(self.id) + "\n")
        # file.write("vector_size,"+str(self.vector_size) + "\n")
        # file.write("context_window_size,"+str(self.context_window_size) + "\n")
        # file.write("skip_gram,"+str(self.skip_gram) + "\n")
        # file.write("hs,"+str(self.hs) + "\n")
        # file.write("negative,"+str(self.negative) + "\n")
        # file.write(","+str(self.iter) + "\n")
        # file.write("iter,"+str(self.min) + "\n")
        # file.write("max,"+str(self.max) + "\n")
        # file.write("ngram,"+str(self.ngram) + "\n")
        file.close()
