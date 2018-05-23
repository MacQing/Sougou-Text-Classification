# -*- coding: utf-8 -*-
# @Time    : 2018/5/23 22:48
# @Author  : yindaqing
# @Email   : medichen@foxmail.com
# @File    : analyzer.py
# @Software: PyCharm

import re, jieba

re_han_word = re.compile("^([\u4E00-\u9FD5a-zA-Z0-9+#&\._%]+)$", re.U)

class Analyzer:

    def cut(self, sentence, forSearch=False):
        """
        分词器
        :param sentence:
        :param forSearch:
        :return:
        """
        if forSearch:
            return list(jieba.cut_for_search(sentence))
        else:
            return list(jieba.cut(sentence))

    def filter(self, tokens):
        """
        过滤器：过滤掉包含字符的token
        :param self:
        :param tokens:
        :return:
        """
        return [tk for tk in tokens if re.match(re_han_word, tk)]

    def cutAndFilter(self, sentence, forSearch=False):
        """
        分词+过滤
        :param sentence:
        :param forSearch:
        :return:
        """
        return self.filter(self.cut(sentence, forSearch))

if __name__ == '__main__':
    analyzer = Analyzer()
    print(analyzer.cutAndFilter('我爱中华人民共和国，s5700-s是一款路由器\n'))