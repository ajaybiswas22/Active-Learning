from utility.loaders import *
from utility.otherUtility import collapseString


def labelingBase(comment: str, n_gram=1):
    negative = textLoader("biasedNgrams-base/negative" +
                          str(n_gram)+"Gram.txt", "str")
    positive = textLoader("biasedNgrams-base/positive" +
                          str(n_gram)+"Gram.txt", "str")

    for ngram in negative:
        if collapseString(ngram) in collapseString(comment):
            return 0
    for ngram in positive:
        if collapseString(ngram) in collapseString(comment):
            return 1
    return 0.5


def labelingExpanded(comment: str, n_gram=1):
    negative = textLoader("biasedNgrams-expanded/negative" +
                          str(n_gram)+"Gram.txt", "str")
    positive = textLoader("biasedNgrams-expanded/positive" +
                          str(n_gram)+"Gram.txt", "str")

    for ngram in negative:
        if collapseString(ngram) in collapseString(comment):
            return 0
    for ngram in positive:
        if collapseString(ngram) in collapseString(comment):
            return 1
    return 0.5
