# -*- coding: utf-8 -*-
# @Time    : 2018/5/22 23:56
# @Author  : yindaqing
# @Email   : medichen@foxmail.com
# @File    : esProxy.py
# @Software: PyCharm

import logging
from elasticsearch import Elasticsearch

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__file__)

esHost, esPort = 'localhost', '9200'

def getDataFromEs():
    queryResult = []

    es = Elasticsearch(hosts=[dict(host=esHost, port=esPort)])

    # 分页大小，游标过期时间
    size = 100
    scrollTime = '10s'

    # 游标分页查询
    queryBody = {
                  "query": {
                    "bool": {
                      "filter": {
                        "exists": {
                          "field": "doc_type"
                        }
                      }
                    }
                  },
                "sort": ["_doc"],
                "size": size
                }
    # 记录当前分页的页码
    page = 1
    try:
        esHits = es.search(index='sougou_news', doc_type='sougou_news', body=queryBody, scroll=scrollTime)
        if not esHits['hits']['hits']:
            return queryResult
        queryResult.extend([d['_source'] for d in esHits['hits']['hits']])
        logger.info('ES查询数据中. page=%d, sizeTotal=%d' % (page, len(queryResult)))
        page = page + 1

        scrollId = esHits['_scroll_id']
        while True:
            esHits = es.scroll(scroll_id=scrollId, scroll=scrollTime)
            if not esHits['hits']['hits']:
                return queryResult
            queryResult.extend([d['_source'] for d in esHits['hits']['hits']])
            logger.info('ES查询数据中. page=%d, sizeTotal=%d' % (page, len(queryResult)))
            page = page + 1

            # 更新scrollId
            scrollId = esHits['_scroll_id']
    except Exception as e:
        logger.info('ES查询异常. %s' % (str(e)))

    return esHits

if __name__ == '__main__':
    esHits = getDataFromEs()