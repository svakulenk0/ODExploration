'''
svakulenko
17 Jan 2017

Ranking for nodes and chunks of the information model
'''
from Queue import PriorityQueue
from heapq import heappush, nlargest

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


def chunk_w_ranks(facets, entities):
    chunks = []

    # facets chunk
    facets_chunk = []
    for facet, count in facets.items():
        heappush(facets_chunk, (n_items/count['value'], facet))
        # facets_chunk[facet] = n_items / count['value']
    # print facets_chunk
    chunks.append(facets_chunk)

    # entities chunk per facet
    for facet, counts in entities.items():
        facet_chunk = []
        entities = counts['buckets']
        # save facet rank
        heappush(facet_chunk, (n_items/facets[facet]['value'], facet))
        # iterate over entities of the facet
        for entity in entities:
            heappush(facet_chunk, (entity['doc_count'], entity['key']))
        # print facets_chunk
        chunks.append(facet_chunk)
    return chunks


def rank_chunks(chunks, l):
    '''
    ranks chunks by the total rank of the top l concepts
    l <int> limit of the cognitive resource defining the size of the chunk per message
    history <list> set of nodes already transmitted
    '''
    concept_rank = []
    for chunk in chunks:
        chunk_sum = 0
        concepts = []
        for rank, concept in nlargest(l, chunk):
            chunk_sum += rank
            concepts.append(concept)
        heappush(concept_rank, (chunk_sum, concepts))
    return concept_rank


def test_rank_chunks(l=4):
    chunks = chunk_w_ranks(facets, entities)
    chunks_rank = rank_chunks(chunks, l)
    message = nlargest(1, chunks_rank)[0][1]
    print message


def test_chunk(n=2):
    print chunk(facets, entities)[:n]


def test_chunk_w_ranks(n=2):
    print chunk_w_ranks(facets, entities)[:n]


def test_rank_nodes(topn=20):
    ranking = rank_nodes(facets, entities)
    for i in range(topn):
        print ranking.get()


def main():
    test_rank_chunks()


if __name__ == '__main__':
    main()
