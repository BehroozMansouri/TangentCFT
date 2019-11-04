class Configuration:
    def __init__(self, config_file_path=None):
        """
        Configuration for the n-gram embedding model, FastText.
        :param config_file_path: Read configs from the given path, if set to None all the parameters will be set to
        None, so that they can be set in the program manually.
        """
        self.context_window_size = None
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
        """
        Saves configuration of the model in a file.
        :param config_file_path: File path where the model's configuration are saved.
        """
        file = open(config_file_path, "w")
        attribute_map = self.__dict__
        for item in attribute_map:
            file.write(item + "," + str(attribute_map[item]) + "\n")
        file.close()
