'''
svakulenko
12 Dec 2017

Create sample utterances from data
'''
from Queue import PriorityQueue
from collections import defaultdict

from load_ES import ESClient
from aggregations import counts, top_keywords


def list_facets_counts():
    '''
    counts of entities for each attribute
    '''
    stats = []
    for facet, count in counts.items():
        stats.append("%s %s" % (count['value'] , facet))

    stats_string = "There are " + ", ".join(stats)
    print stats_string


def facets_top_entities(k=2):
    '''
    top entities for each attribute
    '''
    stats = []
    for facet, count in top_keywords.items():
        top_entities = []
        for rank in range(k):
            top_entities.append(count['buckets'][rank]['key'])

        stats.append("%s are the most popular among %s" % (" and ".join(top_entities), facet))

    stats_string = "\n".join(stats)
    print stats_string


def sample_items(attribute, entity, size):
    '''
    show a sample of items for an entity
    '''
    db = ESClient()
    results = db.search_by(field=attribute, value=entity, limit=size)
    for item in results:
        print item["_source"]["raw"]["title"]


def rank_nodes(top_keywords):
    '''
    rank nodes by degree (counts)
    '''
    # initialize a priority queue to store nodes ranking
    q = PriorityQueue()
    #  iterate over attributes
    for facet, counts in top_keywords.items():
        entities = counts['buckets']
        # iterate over top entities of the attribute
        for entity in entities:
            # insert into the priority queue (max weight items to go first)
            q.put((-entity['doc_count'], (facet, entity['key'])))
    return q


TEMPLATES = {
                'single': ["%s is the most popular %s"],
                'multiple': [
                        "The most popular %s are: %s",
                        "%s are the most popular among %ss"
                    ],
                'join': [", ", " and "],
            }


def test_rank_nodes(topn=20):
    ranking = rank_nodes(top_keywords)
    
    # group topn ranked nodes by attribute
    top_facets = defaultdict(list)

    for i in range(topn):
        # unpack rank
        weight, relation = ranking.get()
        facet, entity = relation
        top_facets[facet].append(entity)
    
    # phrase topn ranked nodes
    for facet, entities in top_facets.items():
        if len(entities) > 1:
            print TEMPLATES['multiple'][0] % (TEMPLATES['join'][0].join(entities), facet)
        else:
            print TEMPLATES['single'][0] % (entities[0], facet)


def test_sample_items():
    sample_items(attribute="raw.license_id.keyword", entity="cc-by-at-30", size=5)


def main():
    test_rank_nodes()


if __name__ == '__main__':
    main()
