# Classification of Comments Supporting the Indian Farmers’ Protest Using Active Learning and Weak Supervision

The introduction of farm bills 2020 was seen as a major agricultural reform. However, started a year-long protest which finally ended with the repeal of the bills. In this work, the authors tried to classify YouTube comments into those that are in support of the farm bill and those that are against it. A total of 1076 unique videos were gathered from YouTube, consisting of a total of 178,608 comments, out of which 20,024 comments were used to form the corpus. The authors proposed a batch-wise random sampling and uncertainty sampling technique that significantly reduced labeling costs by 75\% with decent accuracy. For performing classification, four classifiers were incorporated, i.e., Logistic Regression, Support Vector Machines (SVM), K-Nearest Neighbors (KNN), and Multi-Layer Perceptron (MLP), along with FastText for Word Embeddings. Among these four classifiers, SVM and MLP performed the best, with 82.64\% and 82.18\% accuracy, respectively. The results of the KNN classifier were further improved to 72.66\% after performing Weak Classification combined with Uncertainty Sampling.
