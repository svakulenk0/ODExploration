'''
svakulenko
17 Jan 2017

Ranking for nodes and chunks of the information model
'''
from Queue import PriorityQueue

from aggregations import facets, entities, n_items


def rank_nodes(facets, entities):
    '''
    rank nodes from the database stats
    '''
    # initialize a priority queue to store nodes ranking
    q = PriorityQueue()

    # rank facets
    for facet, count in facets.items():
        q.put((- n_items / count['value'], facet))

    #  rank entities
    for facet, counts in entities.items():
        entities = counts['buckets']
        # print facet, len(entities)
        # iterate over entities of the facet
        for entity in entities:
            # insert into the priority queue (max weight items to go first)
            q.put((- entity['doc_count'], (facet, entity['key'])))
    return q


def chunk(facets, entities):
    chunks = []

    # facets chunk
    facets_chunk = [facet for facet, count in facets.items()]
    # print facets_chunk
    chunks.append(facets_chunk)

    # entities chunk per facet
    for facet, counts in entities.items():
        entities = counts['buckets']
        # iterate over entities of the facet
        facet_chunk = [entity['key'] for entity in entities]
        # print facets_chunk
        chunks.append(facet_chunk)
    return chunks


def rank_chunks(facets, entities):
    chunks = []

    # facets chunk
    facets_chunk = [facet for facet, count in facets.items()]
    # print facets_chunk
    chunks.append(facets_chunk)

    # entities chunk per facet
    for facet, counts in entities.items():
        entities = counts['buckets']
        # iterate over entities of the facet
        facet_chunk = [entity['key'] for entity in entities]
        # print facets_chunk
        chunks.append(facet_chunk)
    return chunks


def test_chunk(n=2):
    print chunk(facets, entities)[:n]


def test_rank_nodes(topn=20):
    ranking = rank_nodes(facets, entities)
    for i in range(topn):
        print ranking.get()


def main():
    test_chunk()


if __name__ == '__main__':
    main()
