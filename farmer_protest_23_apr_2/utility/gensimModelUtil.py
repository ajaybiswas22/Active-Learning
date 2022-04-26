from gensim.models import Word2Vec
from utility.twokenize import tokenizeRawTweetText as tknzr
import numpy as np


class Word2VecUtil():
    def __init__(self,
                 path: str
                 ):
        self.model = Word2Vec.load(path)

    def getWordEmbedding(self,
                         word: str
                         ):
        try:
            return self.model.wv[word]
        except KeyError:
            return np.asarray(np.zeros(self.model.wv['a'].shape))
