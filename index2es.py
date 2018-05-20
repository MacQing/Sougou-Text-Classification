# -*- coding: utf-8 -*-
# @Time    : 2018/5/20 12:36
# @Author  : yindaqing
# @Email   : medichen@foxmail.com
# @File    : index2es.py
# @Software: PyCharm

import io
from collections import defaultdict
from elasticsearch import Elasticsearch
import StringUtils

sougouTceTxt = 'data/SogouTCE.txt'
newsSohusiteXmlDat = 'data/news_sohusite_xml.dat'

class SougouXmlFile(io.TextIOWrapper):
    def __init__(self, filename, mode, encoding):
        self.file = open(filename, mode=mode, encoding=encoding)
        super().__init__(self.file.buffer)

        self.DOC_PRE = '<doc>'
        self.DOC_POST = '</doc>'
        self.URL_PRE = '<url>'
        self.URL_POST = '</url>'
        self.DOCNO_PRE = '<docno>'
        self.DOCNO_POST = '</docno>'
        self.CONTENTTITLE_PRE = '<contenttitle>'
        self.CONTENTTITLE_POST = '</contenttitle>'
        self.CONTENT_PRE = '<content>'
        self.CONTENT_POST = '</content>'

    def close(self):
        self.file.close()
        super().close()

    def readDocBlock(self):
        docBlock = None
        while True:
            line = self.file.readline().strip()
            if len(line) == 0:
                return None

            if line == self.DOC_PRE:
                docBlock = defaultdict(str)
            elif line == self.DOC_POST:
                return docBlock
            elif line.startswith(self.URL_PRE) and line.endswith(self.URL_POST):
                docBlock['url'] = line[len(self.URL_PRE) : len(line) - len(self.URL_POST)]
            elif line.startswith(self.DOCNO_PRE) and line.endswith(self.DOCNO_POST):
                docBlock['docno'] = line[len(self.DOCNO_PRE) : len(line) - len(self.DOCNO_POST)]
            elif line.startswith(self.CONTENTTITLE_PRE) and line.endswith(self.CONTENTTITLE_POST):
                docBlock['contenttitle'] = line[len(self.CONTENTTITLE_PRE) : len(line) - len(self.CONTENTTITLE_POST)]
            elif line.startswith(self.CONTENT_PRE) and line.endswith(self.CONTENT_POST):
                docBlock['content'] = line[len(self.CONTENT_PRE) : len(line) - len(self.CONTENT_POST)]

"""
载入文档类型词典
key: url前缀
value: 文档类型
"""
def loadDocTypeDict():
    typeDict = defaultdict(str)
    with open(sougouTceTxt, 'r', encoding='gb18030') as f:
        for line in f.readlines():
            splitedLine = line.strip().split('\t')
            if len(splitedLine) == 2:
                typeDict[splitedLine[0]] = splitedLine[1]
    return typeDict

"""
根据url判断文档类型
"""
def getDocTypeByUrl(url, docTypeDict):
    for urlPrefix, docType in docTypeDict.items():
        if url.startswith(urlPrefix):
            return docType
    return None

def index2es():
    es = Elasticsearch(hosts=[{'host': 'localhost', 'port': '9200'}])
    indexName = 'sougou_news'
    typeName = 'sougou_news'

    docTypeDict = loadDocTypeDict()

    with SougouXmlFile(newsSohusiteXmlDat, mode='r', encoding='gb18030') as f:
        blockNo = 1
        while True:
            block = f.readDocBlock()
            if block is None:
                break

            id = block['docno']
            if len(id) == 0:
                continue

            data = dict(doc_id=block['docno'],
                        doc_url=block['url'],
                        doc_title=StringUtils.strQ2B(block['contenttitle']),
                        doc_content=StringUtils.strQ2B(block['content']),
                        doc_type=getDocTypeByUrl(block['url'], docTypeDict))

            es.index(index=indexName, doc_type=typeName, id=id, body=data)
            print('No-%d: type=%s, title=%s' % (blockNo, data['doc_type'], data['doc_title']))

            blockNo = blockNo + 1


if __name__ == '__main__':
    index2es()