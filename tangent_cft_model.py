from gensim.models import FastText
import datetime


class tangent_cft_model:
    def __init__(self, config, fast_text_train_data):
        self.FastTextInput = fast_text_train_data
        self.config = config
        self.model = None

    def train(self):
        """
            This method trains the fastText model based on the specified config file
            After setting fastText hyper-parameters, it reads Wikipedia dataset and add the tuples converted char values to model words.
            Suppose that a formula is consists of tuples ABC,DEF,GHI they are fed to fastText as {ABC,DEF,GHI}.
        """
        size = self.config.vector_size
        window = int(self.config.context_window_size)
        sg = int(self.config.skip_gram)
        hs = int(self.config.hs)
        negative = int(self.config.negative)
        iteration = int(self.config.iter)
        min_n = int(self.config.min)
        max_n = int(self.config.max)
        word_ngrams = int(self.config.ngram)

        train_start_time = datetime.datetime.now()

        self.model = FastText(self.FastTextInput, size=size, window=window, sg=sg, hs=hs,
                              workers=1, negative=negative, iter=iteration, min_n=min_n,
                              max_n=max_n, word_ngrams=word_ngrams)

        "return model train time"
        train_end_time = datetime.datetime.now()
        return train_end_time -train_start_time

    def get_vector(self, math_concept):
        return self.model.wv[math_concept]
