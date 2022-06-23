from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import make_pipeline
import numpy as np

class FastTextTransformer(BaseEstimator, TransformerMixin):
    """ Convert texts into their mean fastText vectors """

    def __init__(self, model):
        self.model = model

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return np.stack([np.mean([self.model[w] for w in text.split()], 0) for text in X])


def classify(small_model, predictor, lines, Y):
    classifier = make_pipeline(
        FastTextTransformer(model=small_model),
        predictor
    ).fit(
        lines,
        Y
    )
    return classifier


def FAST(texts, model):
    return np.stack([np.mean([model[w] for w in text.split()], 0) for text in texts])
