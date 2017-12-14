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

    def __init__(self, top_keywords=top_keywords):
        # keep track of the last transmitted node attribute to save space in the bucket
        self.top_keywords = top_keywords
        # normalization constant for estimating the total information space size
        self.space_size = 10140

    def report_message_stats(self):
        self.transmitted_messages += 1
        print "\t", self.sum_weight / self.transmitted_symbols, "information units per symbol"
        print "\t", self.sum_weight / self.transmitted_messages, "information units per message"
        print "\t%.2f% of the information space communicated" % (self.sum_weight / float(self.space_size))

    def transmit(self, message, report=False):
        '''
        simulate communication channel
        '''
        if message not in self.transmitted_node:
            # report previous node as a message
            if self.transmitted_symbols and report:
                self.report_message_stats()
            print message
            return len(message)
        return 0

    def communicate_node(self, node):
        transmitted_symbols = 0
        weight, relation = node
        facet, entity = relation
        transmitted_symbols += self.transmit(facet, True)
        transmitted_symbols += self.transmit(entity)
        self.sum_weight -= weight

        self.transmitted_symbols += transmitted_symbols
        self.transmitted_node = relation

        # report current communication efficiency (knowledge flow velocity/productivity) per symbol
        # print - weight / transmitted_symbols

    def tell_story(self, topn=10):
        '''
        Runs the simulation of the knowledge flow
        simultaneously evaluating its productivity (velocity of the chanel)

        topn <int> defines the size of the story requested in terms of the number of concepts communicated
        '''
        self.ranking = rank_nodes(self.top_keywords)
        # initialize story stats
        self.sum_weight = 0
        self.transmitted_node = []
        self.transmitted_symbols = 0
        self.transmitted_messages = 0
        
        self.tell_clusters(topn)
        # report final message
        self.report_message_stats()

        # report story stats
        print "\nTotal: communicated", self.sum_weight, "information units via", self.transmitted_symbols, "symbols in", self.transmitted_messages, "messages"

    def tell_clusters(self, topn):
        '''
        Clustering approach to storytelling is based on an optimistic assumption that the conversation will last at least k number of turns.
        This way the agent can design an optimal combination of entities assuming k number of turns is available.
        '''
        
        # group topn ranked nodes by attribute
        clusters = defaultdict(list)
        facet_queue = []

        # cluster entities around facets
        for i in range(topn):
            # unpack rank
            transmitted_symbols = 0
            # retrieve the node
            weight, relation = self.ranking.get()
            facet, entity = relation
            clusters[facet].append((weight, relation))
            if facet not in facet_queue:
                facet_queue.append(facet)

        # process top clusters
        for facet in facet_queue:
            for node in clusters[facet]:
                self.communicate_node(node)
            # communicate one cluster per message
            # self.transmitted_messages += 1
            # print "\t", self.sum_weight / self.transmitted_symbols, "information units per symbol"
            # print "\t", self.sum_weight / self.transmitted_messages, "information units per message"

    def tell_greedy(self, topn):
        '''
        Greedy approach to storytelling based on the pessimistic assumption that the conversation can be interupted any time.
        '''
        # iterate over top n entities
        for i in range(topn):
            # retrieve the node
            self.communicate_node(self.ranking.get())


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
    chatbot = DialogAgent()
    chatbot.tell_story(story_size)


def main():
    test_story_teller()


if __name__ == '__main__':
    main()
