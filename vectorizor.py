# -*- coding: utf-8 -*-
# @Time    : 2018/5/29 22:32
# @Author  : yindaqing
# @Email   : medichen@foxmail.com
# @File    : vectorizor.py
# @Software: PyCharm

import numpy as np


class TfidfVectorizor(object):
    def __init__(self, tfidfVectorizor, fields):
        """
        :param tfidfVectorizor:
        :param fields: 待向量化的属性list
        :return:
        """
        self.tfidfVectorizors = tfidfVectorizor
        self.fields = fields

    def fit(self, X=None, y=None):
        return self

    def transform(self, X):
        """
        将每个属性向量化后，拼接成一个向量
        """
        vectors = None
        for i, field in enumerate(self.fields):
            docs = [x[field] for x in X]
            vector = self.tfidfVectorizors.transform(docs)
            vectors = np.hstack(vectors, vector) if i > 0 else vector
        return vectors


class Doc2VecVectorizor(object):
    def __init__(self, word2vec, fields):
        self.word2vec = word2vec
        self.size = word2vec.vector_size
        self.fields = fields

    def fit(self, X=None, y=None):
        return self

    def transform(self, X):
        """
        计算文档的特征向量
        1. 对每个属性，计算每个词的vector，然后将所有词的vector的平均值作为该属性的vector
        2. 所有属性的vector，flatten为一个宽vector，作为该文档的特征向量
        """
        return np.array([self.__doc2vec(x) for x in X])

    def __sentence2vec(self, sentence):
        if len(sentence.strip()) == 0:
            return np.zeros(self.size)
        vectors = [self.word2vec[word] if word in self.word2vec else np.zeros(self.size) for word in sentence.split()]
        return np.mean(vectors, axis=0)

    def __doc2vec(self, doc):
        vectors = np.array([self.__sentence2vec(doc[field]) for field in self.fields])
        return vectors.flatten()
