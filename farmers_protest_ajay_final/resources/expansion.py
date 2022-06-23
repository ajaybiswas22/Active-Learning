import fasttext
import copy
import numpy as np
import pandas as pd
import math

from resources.fasttext_transformer import classify

def Expand_U(model: fasttext.FastText._FastText,
             algorithm: object,
             seed_set_tokenised: list,
             seed_set_label: list,
             expansion_tokenised: list,
             expansion_set_labels: list,
             batch_size: int,
             countMax: int):
    """ Uncertainty sampling.
    Expand seed set using expansion_set based on lowest confidance scores.
    max_threshold: max. probability for uncertainty selection """

    seed_TK = copy.deepcopy(seed_set_tokenised)
    seed_labels = copy.deepcopy(seed_set_label)
    count = len(expansion_set_labels)
    M = np.arange(0, count, batch_size)

    # exp_TK_certain will be the list of comments having high proba score
    exp_TK_certain = []
    exp_TK_certain_labels = []

    for i in range(1, len(M)):

        #print(M[i], end=' ')

        exp_TK = expansion_tokenised[M[i-1]:M[i]]
        exp_labels = expansion_set_labels[M[i-1]:M[i]]

        # take A as training and B as test and store probs in C
        small_model = classify(model,algorithm,seed_TK,seed_labels)
        #small_model = algorithm.fit(seed_TK, seed_labels)
        # store classwise prob. scores
        C = small_model.predict_proba(exp_TK)
        # Uncertainty sampling scores
        C_abs_diff = [(abs(x[0] - x[1])) for x in C]

        # Sort lists in ascending order of probabilities from C_abs_diff
        sorted_lists = sorted(
            zip(exp_labels, exp_TK, C, C_abs_diff), key=lambda x: x[3])
        exp_labels, exp_TK, C_sorted, score = [
            [x[i] for x in sorted_lists] for i in range(4)]

        Y_uncertain = []
        exp_TK_uncertain = []
        for j in range(len(C_sorted)):
            max_value = max(C_sorted[j])
            max_index = str(np.argmax(C_sorted[j]))

            # label the comments whose score is less than threshold
            if(j < countMax):

                exp_TK_uncertain.append(exp_TK[j])
                Y_uncertain.append(exp_labels[j])
            else:
                exp_TK_certain.append(exp_TK[j])
                exp_TK_certain_labels.append(exp_labels[j])

        # expand the seed set
        seed_labels.extend(Y_uncertain)
        seed_TK.extend(exp_TK_uncertain)

    return seed_TK, seed_labels, exp_TK_certain, exp_TK_certain_labels

def n_gram_count(sentence: str, n_gram_phrase: str):
    return sentence.count(n_gram_phrase)


def IDF(corpus, unique_words):
   idf_dict = {}
   N = len(corpus)
   for i in unique_words:
     count = 0
     for sen in corpus:
       if n_gram_count(sen, i) != 0:
         count = count+1
       idf_dict[i] = (math.log((1+N)/(count+1)))+1
   return idf_dict


def TF(sentence, n_gram_phrase, unique_words):
    """count of t in d / number of words in d

       each phrase in unique_words is considered as a word
    """
    freq = n_gram_count(sentence, n_gram_phrase)
    total_words = len(sentence.split())
    remove = 0
    for word in unique_words:
      freq_word = n_gram_count(sentence, word)
      word_count = freq_word * len(word.split())
      freq_word = word_count - freq_word
      remove += freq_word
    total_words -= remove
    return freq/total_words


def corpus_unique(corpus, n_gram_words):
  """ returns the total unique words in corpus """
  all_sentences = (' '.join(corpus))
  all_words = list(set(all_sentences.split()))
  all_words.extend(n_gram_words)

  return list(set(all_words))


def WeakFeatures(lines, n_gram_words):

    F = np.zeros((len(lines), len(n_gram_words)))

    comments_list = list(lines)

    IDF_dict = IDF(lines, n_gram_words)
    corpus_words = corpus_unique(comments_list, n_gram_words)

    for i in range(len(comments_list)):
        for j in range(len(n_gram_words)):
            #F[i][j] = TF(comments_list[i], n_gram_words[j],corpus_words)*IDF_dict[n_gram_words[j]]
            if n_gram_count(comments_list[i], n_gram_words[j]) != 0:
                F[i][j] = 1
            else:
                F[i][j] = 0
    return F

def Expand_UW(model: fasttext.FastText._FastText,
             algorithm: object,
             seed_set_tokenised: list,
             seed_set_label: list,
             expansion_tokenised: list,
             expansion_set_labels: list,
             batch_size: int,
             countMax: int,
             n_gram_words):
    """ Uncertainty sampling.
    Expand seed set using expansion_set based on lowest confidance scores.
    max_threshold: max. probability for uncertainty selection """

    seed_TK = copy.deepcopy(seed_set_tokenised)
    seed_labels = copy.deepcopy(seed_set_label)
    count = len(expansion_set_labels)
    M = np.arange(0, count, batch_size)

    # exp_TK_certain will be the list of comments having high proba score
    exp_TK_certain = []
    exp_TK_certain_labels = []

    for i in range(1, len(M)):

        #print(M[i], end=' ')

        exp_TK = expansion_tokenised[M[i-1]:M[i]]
        exp_labels = expansion_set_labels[M[i-1]:M[i]]

        # Weak supervision
        F = WeakFeatures(seed_TK, n_gram_words)

        # transform
        X = np.stack([np.mean([model[w] for w in text.split()], 0)
                      for text in seed_TK])

        # join them
        XF = np.hstack((X, F))

        # Weak supervision
        FT = WeakFeatures(exp_TK, n_gram_words)

        # transform
        XT = np.stack([np.mean([model[w] for w in text.split()], 0)
                       for text in exp_TK])

        # join them
        XFT = np.hstack((XT, FT))

        small_model = algorithm.fit(XF, seed_labels)

        # take A as training and B as test and store probs in C
        #small_model = classify(model, algorithm, seed_TK, seed_labels)
        # store classwise prob. scores
        C = small_model.predict_proba(XFT)
        # Uncertainty sampling scores
        C_abs_diff = [(abs(x[0] - x[1])) for x in C]

        # Sort lists in ascending order of probabilities from C_abs_diff
        sorted_lists = sorted(
            zip(exp_labels, exp_TK, C, C_abs_diff), key=lambda x: x[3])
        exp_labels, exp_TK, C_sorted, score = [
            [x[i] for x in sorted_lists] for i in range(4)]

        Y_uncertain = []
        exp_TK_uncertain = []
        for j in range(len(C_sorted)):
            max_value = max(C_sorted[j])
            max_index = str(np.argmax(C_sorted[j]))

            # label the comments whose score is less than threshold
            if(j < countMax):

                exp_TK_uncertain.append(exp_TK[j])
                Y_uncertain.append(exp_labels[j])
            else:
                exp_TK_certain.append(exp_TK[j])
                exp_TK_certain_labels.append(exp_labels[j])

        # expand the seed set
        seed_labels.extend(Y_uncertain)
        seed_TK.extend(exp_TK_uncertain)

    return seed_TK, seed_labels, exp_TK_certain, exp_TK_certain_labels
