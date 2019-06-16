class configuration:

    def __init__(self, config_file_path=None):
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

        if config_file_path is not None:
            file = open(config_file_path)
            line = file.readline().rstrip('\n')
            while line:
                parameter = line.split(",")[0]
                value = line.split(",")[1]
                if str.isdigit(value):
                    value = int(value)
                setattr(self, parameter, value)
                line = file.readline().rstrip('\n')
            file.close()

    def write_to_file(self, config_file_path):
        file = open(config_file_path, "w")
        attribute_map = self.__dict__
        for item in attribute_map:
            file.write(item + "," + str(attribute_map[item]) + "\n")
        file.close()
