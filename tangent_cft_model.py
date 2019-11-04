from gensim.models import FastText
import datetime


class TangentCftModel:
    def __init__(self,):
        self.model = None

    def train(self, config, fast_text_train_data):
        """
        Takes in the fastText parameters and the train data and trains the FastText model
        :param config: configuration for fastText model
        :param fast_text_train_data: train data
        :return:
        """
        size = config.vector_size
        window = int(config.context_window_size)
        sg = int(config.skip_gram)
        hs = int(config.hs)
        negative = int(config.negative)
        iteration = int(config.iter)
        min_n = int(config.min)
        max_n = int(config.max)
        word_ngrams = int(config.ngram)

        train_start_time = datetime.datetime.now()
        print("Training the model")
        self.model = FastText(fast_text_train_data, size=size, window=window, sg=sg, hs=hs,
                              workers=1, negative=negative, iter=iteration, min_n=min_n,
                              max_n=max_n, word_ngrams=word_ngrams)

        train_end_time = datetime.datetime.now()
        "Returns the train time of the model"
        return train_end_time - train_start_time

    def save_model(self, model_file_path):
        file_name = (model_file_path+".wv.vectors.npy")
        self.model.save(file_name)

    def load_model(self, model_file_path):
        self.model = FastText.load(model_file_path+".wv.vectors.npy")

    def get_vector_representation(self, encoded_math_tuple):
        return self.model.wv[encoded_math_tuple]
