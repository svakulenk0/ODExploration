'''
svakulenko
17 Jan 2017

Ranking for nodes and chunks of the information model
'''
from queue import PriorityQueue
from heapq import heappush, nlargest
import numpy as np

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
            if (facet, concept) not in history:
                chunk_sum += rank
                concepts.append(concept)
            if len(concepts) >= l:
                break
        concept_rank.put((-chunk_sum, (facet, concepts)))
    return concept_rank


def gini(x):
    '''
    Relative mean absolute difference (rmad) / 2
    from https://stackoverflow.com/questions/39512260/calculating-gini-coefficient-in-python-numpy
    '''
    # (Warning: This is a concise implementation, but it is O(n**2)
    # in time and memory, where n = len(x).  *Don't* pass in huge
    # samples!)

    # Mean absolute difference (standard deviation?)
    mad = np.abs(np.subtract.outer(x, x)).mean()
    # Relative mean absolute difference (average)
    mean = np.mean(x)
    # print mean
    rmad = mad/mean
    # Gini coefficient
    g = 0.5 * rmad
    return abs(g)


def gini_facets(entities):
    '''
    analyse skewness of the distribution among the entites within the attribute
    compute a score for each attribute characterizing the skewness
    of the information mass distribution
    to quantify the discriminatory power of the individual factors (attributes)
    '''
    #  iterate over attributes
    # facets_rank = PriorityQueue()
    # for facet, counts in top_keywords.items():
    #     # top entities count distribution of the attribute
    #     distribution = [entity['doc_count'] for entity in counts['buckets']]
    #     # print distribution
    #     skewness = gini(distribution)
    #     facets_rank.put((-skewness, facet))
    # return facets_rank

    # chunks = {}
    # entities chunk per facet
    for facet, counts in entities.items():
        # chunks[facet] = []
        # entities count distribution of the attribute
        distribution = [entity['doc_count'] for entity in counts['buckets']]
        skewness = gini(distribution)
        print( facet, skewness )
        # chunks[facet].append((entity['doc_count'], entity['key']))
    # return chunks


def test_gini_facets():
    gini_facets(entities)


def test_rank_nodes(topn=20):
    ranking = rank_nodes(entities)
    for i in range(topn):
        print( ranking.get() )

def test_chunk(n=2):
    print( chunk(entities)[:n] )


def test_chunk_w_ranks(n=2):
    print( chunk_w_ranks(entities) )


def test_rank_chunks(l=3, n=4, entities=entities):
    '''
    l <int> maximum size of the basket
    n <int> number of turns
    '''
    chunks = chunk_w_ranks(entities)
    history = []
    for i in range(n):
        chunks_rank = rank_chunks(chunks, l, history)
        facet, entities = chunks_rank.get()[1]
        print( facet, entities )
        concepts = [(facet, entity) for entity in entities]
        history.extend(concepts)


def main():
    test_gini_facets()


if __name__ == '__main__':
    main()
