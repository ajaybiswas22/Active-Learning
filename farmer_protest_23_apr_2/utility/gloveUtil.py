import pickle
import numpy as np
from unidecode import unidecode


class GloVeUtil():
    def __init__(self, path: str):
        self.embedDict = self.loadEmbeddingDict(path)

    def loadEmbeddingDict(self, path: str):
        with open(path, "rb") as inp:
            gloveDict = pickle.load(inp)
        return gloveDict

    def getWordEmbedding(self, word: str):
        if word in self.embedDict:
            return self.embedDict[word]
        else:
            return np.average([self.embedDict[unidecode(char)] for char in word], axis=0)
