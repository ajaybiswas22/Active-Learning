import numpy as np
import fasttext
from resources.basicIO import InputOutput as IO
import copy

class Expander(object):

    def NN(model, line, K):
        return model.get_nearest_neighbors(line, k=K)

    def oracleHelp(classdata):
        sums = sum(classdata)
        if(sums == 0):
            return False
        res = any(((ele/sums) >= 0.48 and (ele/sums) <= 0.52) for ele in classdata)
        return res

    def cos_sim(a, b):
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        return dot_product / (norm_a * norm_b)

    def sim(x, y, sim_type='cosine_sim'):
        if(sim_type == 'cosine_sim'):
            return Expander.cos_sim(x, y)

    # find similarity score matrix between A and B
    # pass transpose of B
    def sim_matrix(A, B, sim_type):
        m, p = A.shape
        p, n = B.shape
        C = np.zeros((m, n))
        for i in range(m):
            for j in range(n):
                C[i][j] = Expander.sim(A[i, :], B[:, j], sim_type)
        return C

    # finds similarity score

    def score(model, line, k=10):
        # words contains all the words in the corpus
        lst1 = Expander.NN(model, line, k)
        v1 = []
        l1 = [x[1] for x in lst1]
        l10 = [x[0] for x in lst1]
        for i in range(len(model.words)):
            try:
                v1.append(l10[l1.index(model.words[i])])
            except:
                v1.append(0)
        return v1

    # finds classwise average and returns an array of predicted
    # class labels. labels are classwise labels in ascending order
    def label_avg(X, labels, count, exp_labels=None):

        m, n = X.shape
        if(m != len(labels)):
            return None

        avg_sums = []
        no_labels = len(list(set(labels)))

        for p in range(n):

            column = X[:, p]

            avgs = np.zeros(no_labels)

            for lbl in range(no_labels):
                indices = [ix for ix, label in enumerate(labels) if label == lbl]
                avgs[lbl] = np.mean([column[x] for x in indices])

            if(exp_labels != None and Expander.oracleHelp(avgs)):
                avg_sums.append(exp_labels[p])
                count[0] += 1
            else:
                max_avg_pos = avgs.argmax()
                avg_sums.append(max_avg_pos)

        return avg_sums

    def get_NN(model, lines_TK, k):
        scores = []
        for line in lines_TK:
            scores.append(Expander.score(model, line, k))

        return scores

    def Expand(model_file, 
               seed_set_text, 
               seed_set_labels,
               seed_set_TK,
               expansion_text,
               expansion_text_labels,
               expansion_TK,
               batch_size,
               k,
               out_text_file,
               out_label_file
               ):

        #load model
        model = fasttext.load_model(model_file)

        # select comments from expansion_set in batches
        M = np.arange(0, 800, batch_size)

        seed_TK = copy.deepcopy(seed_set_TK)
        seed_labels = copy.deepcopy(seed_set_labels)
        seed_text = copy.deepcopy(seed_set_text)

        count2 = [0]
        for i in range(1, len(M)):

            exp_TK = expansion_TK[M[i-1]:M[i]]
            exp_labels = expansion_text_labels[M[i-1]:M[i]]

            # find NN
            seed_NN = Expander.get_NN(model, seed_TK, k)
            exp_NN = Expander.get_NN(model, exp_TK, k)

            A = np.array(seed_NN)
            B = np.array(exp_NN).T
            C = Expander.sim_matrix(A, B, 'cosine_sim')
            Y = Expander.label_avg(C, seed_labels, count2, exp_labels)
            seed_labels += Y
            seed_TK += exp_TK
            seed_text += expansion_text[M[i-1]:M[i]]

        IO.save_text(out_text_file, seed_text)
        IO.save_text(out_label_file, map(str, seed_labels))


    

    
