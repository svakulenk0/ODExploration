'''
svakulenko
7 Aug 2017

Get (graph) data from Lucene (ES)
'''
import json

from elasticsearch import Elasticsearch


INDEX = 'odexploration'


class ESClient():

    def __init__(self, index):
        self.es = Elasticsearch()
        self.index = index


    def check_n_items(self):
        res = self.es.search(index=self.index, body={"query": {"match_all": {}}})
        print("Total: %d items" % res['hits']['total'])


    def show_one(self):
        result = self.es.search(index=self.index, body={"query": {"match_all": {}}})['hits']['hits'][0]
        print json.dumps(result, indent=4, sort_keys=True)

    def aggregate(self):
        '''
        returns the most popular keywords
        '''
        result = self.es.search(index=self.index, body={"query": {"match_all": {}}, "aggs": {
                "licenses": {"terms": {"field": "raw.license_id.keyword"}},
                "categories": {"terms": {"field": "raw.categorization.keyword"}},
                "tags": {"terms": {"field": "raw.tags.name.keyword"}},
                "organizations": {"terms": {"field": "raw.organization.name.keyword"}}
            }})
        return result['aggregations']


def test_index(index=INDEX):
    db = ESClient(index)
    db.check_n_items()
    # db.show_one()


def test_aggregation_stats(index=INDEX):
    db = ESClient(index)
    print db.aggregate()


if __name__ == '__main__':
    test_aggregation_stats()
