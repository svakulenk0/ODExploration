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
                        "The most popular %ss are: %s",
                        "%s are the most popular among %ss"
                    ],
                'join': [", ", " and "],
            }


def build_sentence(facet, entities, pattern=None):
    '''
    Function to build a sentence using data from the pre-defined templates
    '''
    if len(entities) > 1:
        sentence = TEMPLATES['multiple'][0] % (facet, TEMPLATES['join'][0].join(entities))
    else:
        sentence = TEMPLATES['single'][0] % (entities[0], facet)

    return sentence


def test_rank_nodes(topn=20):
    ranking = rank_nodes(top_keywords)
    for i in range(topn):
        print ranking.get()


class DialogAgent():
    '''
    Chatbot talking data optimizing for knowledge transfer
    '''

    def __init__(self):
        # keep track of the last transmitted node attribute to save space in the bucket
        self.transmitted_node = []
        self.transmitted_symbols = 0

    def transmit(self, message):
        '''
        simulate communication channel
        '''
        if message not in self.transmitted_node:
            print message
            return len(message)
        return 0

    def tell_story(self, topn=10, top_keywords=top_keywords):
        '''
        Runs the simulation of the knowledge flow
        simultaneously evaluating its productivity (velocity of the chanel)

        topn <int> defines the size of the story requested in terms of the number of concepts communicated

        '''
        ranking = rank_nodes(top_keywords)
        sum_weight = 0

        for i in range(topn):
            transmitted_symbols = 0
            # retrieve the node
            weight, relation = ranking.get()
            facet, entity = relation

            # communicate the node
            transmitted_symbols += self.transmit(facet)
            transmitted_symbols += self.transmit(entity)
            sum_weight -= weight

            self.transmitted_symbols += transmitted_symbols
            self.transmitted_node = relation

            # report current communication efficiency (knowledge flow velocity/productivity) per symbol
            # print - weight / transmitted_symbols
            print "\t", sum_weight / self.transmitted_symbols, "information units per symbol"

        print "Total: communicated", sum_weight, "information units via", self.transmitted_symbols, "symbols"
        # print sum_weight / self.transmitted_symbols, "information units per symbol"


def get_top_nodes(topn=20):
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
        print build_sentence(facet, entities)


def test_sample_items():
    sample_items(attribute="raw.license_id.keyword", entity="cc-by-at-30", size=5)


def test_story_teller():
    story_size = 10  # n_concepts
    bot = DialogAgent()
    bot.tell_story(story_size)


def main():
    test_story_teller()


if __name__ == '__main__':
    main()
