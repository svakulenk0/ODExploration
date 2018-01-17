'''
svakulenko
17 Jan 2017

Ranking for nodes and chunks of the information model
'''
from Queue import PriorityQueue
from heapq import heappush, nlargest

from aggregations import entities, n_items


def rank_nodes(entities):
    '''
    rank nodes from the database stats
    '''
    # initialize a priority queue to store nodes ranking
    q = PriorityQueue()

    # rank facets
    # for facet, count in facets.items():
    #     q.put((- n_items / count['value'], facet))

    #  rank entities
    for facet, counts in entities.items():
        entities = counts['buckets']
        # print facet, len(entities)
        # iterate over entities of the facet
        for entity in entities:
            # insert into the priority queue (max weight items to go first)
            q.put((- entity['doc_count'], (facet, entity['key'])))
    return q


def chunk(entities):
    chunks = []

    # facets chunk
    # facets_chunk = [facet for facet, count in facets.items()]
    # print facets_chunk
    # chunks.append(facets_chunk)

    # entities chunk per facet
    for facet, counts in entities.items():
        entities = counts['buckets']
        # iterate over entities of the facet
        facet_chunk = [entity['key'] for entity in entities]
        # print facets_chunk
        chunks.append(facet_chunk)
    return chunks


def chunk_w_ranks(entities):
    chunks = {}

    # facets chunk
    # chunks['facets'] = []
    # for facet, count in facets.items():
    #     chunks['facets'].append((n_items/count['value'], facet))

    # entities chunk per facet
    for facet, counts in entities.items():
        chunks[facet] = []
        entities = counts['buckets']
        # save facet rank
        # chunks[facet].append((n_items/facets[facet]['value'], facet))
        # iterate over entities of the facet
        for entity in entities:
            chunks[facet].append((entity['doc_count'], entity['key']))
    return chunks


def rank_chunks(chunks, l, history=[]):
    '''
    ranks chunks by the total rank of the top l concepts
    l <int> limit of the cognitive resource defining the size of the chunk per message
    history <list> set of nodes already transmitted
    '''
    concept_rank = PriorityQueue()
    for facet, chunk in chunks.items():
        chunk_sum = 0
        concepts = []
        for rank, concept in chunk:
            if concept not in history:
                chunk_sum += rank
                concepts.append(concept)
            if len(concepts) >= l:
                break
        concept_rank.put((-chunk_sum, (facet, concepts)))
    return concept_rank


def test_rank_nodes(topn=20):
    ranking = rank_nodes(entities)
    for i in range(topn):
        print ranking.get()

def test_chunk(n=2):
    print chunk(entities)[:n]


def test_chunk_w_ranks(n=2):
    print chunk_w_ranks(entities)


def test_rank_chunks(l=3, n=2):
    '''
    l <int> maximum size of the basket
    n <int> number of turns
    '''
    chunks = chunk_w_ranks(entities)
    history = []
    for i in range(n):
        chunks_rank = rank_chunks(chunks, l, history)
        message = chunks_rank.get()[1]
        print message
        history.extend(message.values()[0])


def main():
    test_rank_chunks()


if __name__ == '__main__':
    main()
