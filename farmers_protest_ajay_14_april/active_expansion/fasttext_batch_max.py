import numpy as np
import fasttext
from resources.basicIO import InputOutput as IO
import copy
import random


def score(model, line, k):
    # words contains all the words in the corpus
    lst1 = model.get_nearest_neighbors(line, k)
    v1 = []
    l1 = [x[1] for x in lst1]
    l10 = [x[0] for x in lst1]
    for i in range(len(model.words)):
        try:
            v1.append(l10[l1.index(model.words[i])])
        except:
            v1.append(0)
    return v1

def NN(model, line, K):
        return model.get_nearest_neighbors(line, k=K)

def get_NN(model, lines_TK, k):
    scores = []
    for line in lines_TK:
        scores.append(score(model, line, k))
    return scores

def cos_sim(a, b):
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if(norm_a * norm_b == 0.0):
        return dot_product / (norm_a * norm_b + 0.001)
    return dot_product / (norm_a * norm_b)

def sim(x, y, sim_type):
    if(sim_type == 'cosine_sim'):
        return cos_sim(x, y)

# find similarity score matrix between A and B
# pass transpose of B
def sim_matrix(A, B, sim_type):
    m, p = A.shape
    p, n = B.shape
    C = np.zeros((m, n))
    for i in range(m):
        for j in range(n):
            C[i][j] = sim(A[i, :], B[:, j], sim_type)
    return C

def Expand_R(model, seed_set_TK, seed_set_label, expansion_TK, expansion_text_labels, batch_size, count, k, random_rate):
    seed_TK = copy.deepcopy(seed_set_TK)
    seed_labels = copy.deepcopy(seed_set_label)
    M = np.arange(0, count, batch_size)
    cnt = int(random_rate * batch_size)
    count2 = [0]

    for i in range(1, len(M)):

        print(M[i], end=' ')

        exp_TK = expansion_TK[M[i-1]:M[i]]
        exp_labels = expansion_text_labels[M[i-1]:M[i]]

        seed_NN = get_NN(model, seed_TK, k)
        exp_NN = get_NN(model, exp_TK, k)

        A = np.array(seed_NN)
        B = np.array(exp_NN).T
        C = sim_matrix(A, B, "cosine_sim")

        Y_ind = np.argmax(C, axis=0)
        Y = [seed_labels[x] for x in Y_ind]

        if(random_rate == 0.0):
            # no random sampling
            pass
        else:
            # random sampling
            Y_r = random.sample(range(0, len(Y)), cnt)
            for j in Y_r:
                if(Y[j] == exp_labels[j]):
                    count2[0] += 1
                Y[j] = exp_labels[j]

        seed_labels.extend(Y)
        seed_TK.extend(exp_TK)

    return seed_TK, seed_labels, count2


def Expand_A(model, seed_set_TK, seed_set_label, expansion_TK,
             expansion_text_labels, batch_size, count, k, sim_threshold):

    seed_TK = copy.deepcopy(seed_set_TK)
    seed_labels = copy.deepcopy(seed_set_label)
    M = np.arange(0, count, batch_size)

    count2 = [0]

    for i in range(1, len(M)):

        print(M[i], end=' ')

        exp_TK = expansion_TK[M[i-1]:M[i]]
        exp_labels = expansion_text_labels[M[i-1]:M[i]]

        seed_NN = get_NN(model, seed_TK, k)
        exp_NN = get_NN(model, exp_TK, k)

        A = np.array(seed_NN)
        B = np.array(exp_NN).T
        C = sim_matrix(A, B, "cosine_sim")

        Y_ind = np.argmax(C, axis=0)
        Y_val = np.amax(C, axis=0)

        #Y = [seed_labels[x] if y >= sim_threshold else exp_labels[x] for x,y in zip(Y_ind, Y_val)]
        Y = []
        for ii in range(len(Y_ind)):
            if(Y_val[ii] >= sim_threshold):
                Y.append(seed_labels[Y_ind[ii]])
            else:
                Y.append(exp_labels[ii])
                count2[0] += 1

        seed_labels.extend(Y)
        seed_TK.extend(exp_TK)

    return seed_TK, seed_labels, count2


    
