'''
svakulenko
7 Aug 2017

Get (graph) data from Lucene (ES)
'''
import json
import string

from elasticsearch import Elasticsearch


INDEX_LOCAL = 'data_gv_at'
INDEX_SERVER = 'odexploration'
INDEX_CSV = 'autcsv'

INDEX = INDEX_SERVER

N = 2914
N_DOCS = 2028

FACETS = {
    # "dataset_id": "raw.id",
    "tags": "raw.tags.name",
    "categorization": "raw.categorization",
    "title": "raw.title",
    "organization": "raw.organization.name",
    "license": "raw.license_id",
    # "dataset_link": "dataset.dataset_link",
}


class ESClient():

    def __init__(self, index=INDEX, host='localhost', port=9200):
        self.es = Elasticsearch(hosts=[{"host": host, "port": port}])
        self.index = index

    def check_n_items(self):
        res = self.es.search(index=self.index, body={"query": {"match_all": {}}})
        print("Total: %d items" % res['hits']['total'])

    def show_one(self):
        result = self.es.search(index=self.index, body={"query": {"match_all": {}}})['hits']['hits'][0]
        print json.dumps(result, indent=4, sort_keys=True)

    def search(self, keywords, limit=N):
        result = self.es.search(index=self.index, size=limit, body={"query": {"match": {"_all": keywords}}})['hits']['hits']
        return result

    def sample_subset(self, keywords, facet_in, entity, limit=2):
        query = [{"match": {FACETS[facet_in]: entity}}]
        if keywords:
            query.append({"match": {"_all": keywords}})
        result = self.es.search(index=self.index, size=limit,
            body={"query": {"bool": {"must": query}}})['hits']['hits']
        return result

    def describe_subset(self, keywords=None, top_n=N, limit=N):
        '''
        get stats for a subset of the information space
        Returns:
        * field (entity) counts
        * size of the matching subset
        '''
        if keywords:
        # string search
            query = {"match": {"_all": keywords}}
        else:
        # match all docs
            query = {"match_all": {}}
        result = self.es.search(index=self.index, explain=True, size=limit, body={"query": query, "aggs": {
                "title": {"terms": {"field": "raw.title.keyword", "size" : top_n}},
                "license": {"terms": {"field": "raw.license_id.keyword", "size" : top_n}},
                "categorization": {"terms": {"field": "raw.categorization.keyword", "size" : top_n}},
                "tags": {"terms": {"field": "raw.tags.name.keyword", "size" : top_n}},
                "organization": {"terms": {"field": "raw.organization.name.keyword", "size" : top_n}}
            }})
        return result['aggregations'], result['hits']['total']

    def aggregate_entity(self, facet, value, top_n=N, limit=N):
        field = FACETS[facet]
        facets = {
                "title": {"terms": {"field": "raw.title.keyword", "size" : top_n}},
                "license": {"terms": {"field": "raw.license_id.keyword", "size" : top_n}},
                "categorization": {"terms": {"field": "raw.categorization.keyword", "size" : top_n}},
                "tags": {"terms": {"field": "raw.tags.name.keyword", "size" : top_n}},
                "organization": {"terms": {"field": "raw.organization.name.keyword", "size" : top_n}}
                }
        facets.pop(facet, None)
        result = self.es.search(index=self.index, size=limit, q='%s="%s"'%(field, value), body={"aggs": facets})
        return result['aggregations']

    def get_random_doc(self):
        doc = self.es.search(index=self.index, body={
                                  "query": {
                                    "function_score": {
                                      "query": {
                                        "match_all": {}
                                      },
                                      "functions": [
                                        {
                                          "random_score": {}
                                        }
                                      ]
                                    }
                                  }
                                })['hits']['hits'][0]['_source']
        return doc


    def compile_item_entities(self, doc):
        item_entities = []
        for facet, path in FACETS.items():
            # find entity by traversing the dictionary of the item
            entity = doc
            ready = False
            for element in path.split('.'):
                # print element
                if isinstance(entity, list):
                    for e in entity:
                        # item_entities.append(e[element])
                        item_entities.append((facet, e[element]))
                    ready = True
                else:
                    if element in entity.keys():
                        entity = entity[element]
                # print entity
            if not ready and isinstance(entity, str):
                # item_entities.append(entity)
                item_entities.append((facet, entity))
        return item_entities

    def summarize_subset(self, facets_values=[], top_n=N, limit=N):
        '''
        facets_values <dict> of facets and entities to find the subset
        '''
        paths = {
                "title": {"terms": {"field": "raw.title.keyword", "size" : top_n}},
                "license": {"terms": {"field": "raw.license_id.keyword", "size" : top_n}},
                "categorization": {"terms": {"field": "raw.categorization.keyword", "size" : top_n}},
                "tags": {"terms": {"field": "raw.tags.name.keyword", "size" : top_n}},
                "organization": {"terms": {"field": "raw.organization.name.keyword", "size" : top_n}}
                }
        if facets_values:
            # search by entity
            facets = []
            values = []
            # print facets_values
            for facet, value in facets_values:
                field = FACETS[facet]
                facets.append(field)
                # clean up value string: escape ES special characters
                value = value.replace('{', '\{')
                value = value.replace('}', '\}')
                value = value.replace(':', '\:')
                value = value.replace('/', '\/')
                value = value.replace('[', '\[')
                value = value.replace(']', '\]')
                # value = value.encode('utf-8').translate(None, string.punctuation)
                # print value
                values.append(value)
                # query.append({"match": {field: value}})
                # remove facet from aggregation
                paths.pop(facet, None)
            result = self.es.search(index=self.index, size=limit, body={"query": {"query_string":
                                    {"fields": facets, "query": ' '.join(values), "default_operator": "AND"}},
                                     "aggs": paths})
        else:
            # search all
            result = self.es.search(index=self.index, size=limit, body={"query": {"match_all": {}},
                                     "aggs": paths})
        return result

    def search_by(self, facet, value, limit=N):
        field = FACETS[facet]
        result = self.es.search(index=self.index, size=limit, q='%s="%s"'%(field, value))['hits']['hits']
        return result

    def top(self, n=N):
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


def test_describe_subset(index=INDEX, top_n=2):
    db = ESClient(index)
    keyword = "I would like to know more about finanzen"
    results = db.describe_subset(keywords=keyword, top_n=top_n)['aggregations']
    print json.dumps(results, indent=4, sort_keys=True)
    # pick the most representative documents from the subset


def test_top_docs_search(index=INDEX, top_n=2, n_samples=5):
    db = ESClient(index)
    keyword = "stadt wien"
    results = db.describe_subset(keywords=keyword, top_n=top_n)
    # show the top docs
    for item in results['hits']['hits'][:n_samples]:
        print item['_source']['raw']['title']


def test_search(index=INDEX, n_samples=5):
    db = ESClient(index)
    results = db.search("finanzen")
    for result in results[:n_samples]:
        print result['_source']['raw']['categorization']
        print result['_source']['raw']['title']
    print len(results), "results"


def test_search_csv():
    dataset_link = "http://www.data.gv.at/katalog/dataset/80607cc6-8fc1-4b2e-8517-716de8f1ba63"
    print dataset_link
    csv_db = ESClient(INDEX_CSV, host='csvengine', port=9201)
    # csv_db.show_one()
    tables = csv_db.search_by(facet='dataset_link', value=dataset_link)
    if tables:
        print tables[0]['_source']['no_rows'], 'rows'


if __name__ == '__main__':
    test_search_csv()
