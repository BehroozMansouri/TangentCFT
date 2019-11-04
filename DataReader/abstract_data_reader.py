class AbstractDataReader:
    def get_collection(self):
        raise NotImplementedError

    def get_query(self, queries_directory_path):
        raise NotImplementedError
