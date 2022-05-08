import fasttext
import copy
import numpy as np
import pandas as pd

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
        small_model = algorithm.fit(seed_TK, seed_labels)
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
