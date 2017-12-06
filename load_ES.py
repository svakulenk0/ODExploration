'''
svakulenko
7 Aug 2017

Get (graph) data from Lucene (ES)
'''

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


def test_index(index=INDEX):
    db = ESClient(index)
    db.check_n_items()
    db.show_one()


if __name__ == '__main__':
    test_index()
