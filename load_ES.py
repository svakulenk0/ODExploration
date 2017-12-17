'''
svakulenko
7 Aug 2017

Get (graph) data from Lucene (ES)
'''
import json

from elasticsearch import Elasticsearch


INDEX = 'odexploration'


class ESClient():

    def __init__(self, index=INDEX):
        self.es = Elasticsearch()
        self.index = index

    def check_n_items(self):
        res = self.es.search(index=self.index, body={"query": {"match_all": {}}})
        print("Total: %d items" % res['hits']['total'])

    def show_one(self):
        result = self.es.search(index=self.index, body={"query": {"match_all": {}}})['hits']['hits'][0]
        print json.dumps(result, indent=4, sort_keys=True)

    def search(self, keywords):
        result = self.es.search(index=self.index, body={"query": {"match": {"_all": keywords}}})['hits']['hits']
        return result

    def search_by(self, field, value, limit):
        result = self.es.search(index=self.index, size=limit, body={"query": {"match": {field: value}}})['hits']['hits']
        return result

    def top(self, n=2914):
        '''
        returns n most popular entities
        '''
        result = self.es.search(index=self.index, body={"query": {"match_all": {}}, "aggs": {
                "title": {"terms": {"field": "raw.title.keyword", "size" : n}},
                "license": {"terms": {"field": "raw.license_id.keyword", "size" : n}},
                "categorization": {"terms": {"field": "raw.categorization.keyword", "size" : n}},
                "tags": {"terms": {"field": "raw.tags.name.keyword", "size" : n}},
                "organization": {"terms": {"field": "raw.organization.name.keyword", "size" : n}}
            }})
        return result['aggregations']

    def count(self):
        '''
        returns cardinality (number of entities for each of the attributes)
        '''
        result = self.es.search(index=self.index, body={"query": {"match_all": {}}, "aggs": {
                "licenses": {"cardinality": {"field": "raw.license_id.keyword"}},
                "categories": {"cardinality": {"field": "raw.categorization.keyword"}},
                "tags": {"cardinality": {"field": "raw.tags.name.keyword"}},
                "organizations": {"cardinality": {"field": "raw.organization.name.keyword"}}
            }})
        return result['aggregations']


def test_index(index=INDEX):
    db = ESClient(index)
    db.check_n_items()
    # db.show_one()


def test_aggregation_stats(index=INDEX):
    db = ESClient(index)
    print db.top()
    # print db.count()


def test_search(index=INDEX):
    db = ESClient(index)
    results = db.search("finanzen")
    print len(results), "results"
    for result in results:
        print result['_source']['raw']['title']


if __name__ == '__main__':
    test_search()
