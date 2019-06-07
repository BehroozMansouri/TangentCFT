class config:

    def __init__(self, config_file_path):
        file = open(config_file_path)
        self.filepath_fasttext = file.readline().rstrip('\n')
        self.result_file_path = file.readline().rstrip('\n')
        self.vector_size = int(file.readline().rstrip('\n').split(",")[1])
        self.context_window_size = int(file.readline().rstrip('\n').split(",")[1])
        self.skip_gram = int(file.readline().rstrip('\n').split(",")[1])
        self.hs = int(file.readline().rstrip('\n').split(",")[1])
        self.negative = int(file.readline().rstrip('\n').split(",")[1])
        self.iter = int(file.readline().rstrip('\n').split(",")[1])
        self.min = int(file.readline().rstrip('\n').split(",")[1])
        self.max = int(file.readline().rstrip('\n').split(",")[1])
        self.ngram = int(file.readline().rstrip('\n').split(",")[1])
        file.close()