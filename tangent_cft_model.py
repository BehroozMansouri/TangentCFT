from gensim.models import FastText
import os
import datetime

class tangent_cft_model:
    def __init__(self, config):
        self.FastTextInput = []
        self.config = config

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
        iter = int(self.config.iter)
        min_n = int(self.config.min)
        max_n = int(self.config.max)
        word_ngrams = int(self.config.ngram)

        for i in range(1, 17):
            path = self.config.filepath_fasttext + str(i)
            for filename in os.listdir(path):
                file = open(path + "/" + filename)
                line = file.readline()
                lst = []
                while line:
                    line = line.rstrip('\n').strip()
                    if line is not "":
                        lst.append(line)
                    line = file.readline()
                file.close()


                self.FastTextInput.append(lst)
                #####################################################################Rotation
                # for idx in range(1, len(lst)):
                #     self.FastTextInput.append(rotate(lst,1))
                ####################################################################
        print(datetime.datetime.now())
        self.model = FastText(self.FastTextInput, size=size, window=window, sg=sg, hs=hs,
                              workers=1, negative=negative, iter=iter, min_n=min_n,
                              max_n=max_n, word_ngrams=word_ngrams)
        print(datetime.datetime.now())

    def get_vector(self, math_tuple):
        return self.model.wv[math_tuple]

