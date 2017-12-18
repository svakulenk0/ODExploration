'''
svakulenko
12 Dec 2017

Create sample utterances from data
'''
from Queue import PriorityQueue
from collections import defaultdict

import numpy as np
from fuzzywuzzy import fuzz

from load_ES import ESClient, INDEX, FIELDS, N_DOCS
from aggregations import counts, top_keywords, all_keywords
from user_intents import intents, match_intent
from system_actions import actions


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


def gini(x):
    '''
    coefficient of variation (CV) ?
    = Relative mean absolute difference (rmad) / 2
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


def gini_facets(top_keywords):
    '''
    analyse skewness of the distribution among the entites within the attribute
    compute a score for each attribute characterizing the skewness
    of the information mass distribution
    to quantify the discriminatory power of the individual factors (attributes)
    '''
    #  iterate over attributes
    facets_rank = PriorityQueue()
    for facet, counts in top_keywords.items():
        # top entities count distribution of the attribute
        distribution = [entity['doc_count'] for entity in counts['buckets']]
        # print distribution
        skewness = gini(distribution)
        facets_rank.put((-skewness, facet))

    return facets_rank


TEMPLATES = {
                'single': ["%s is the most popular %s"],
                'multiple': [
                        "%s: %s",
                        "The most popular %ss are: %s",
                        "The most popular %ss are: %s",
                        "%s are the most popular among %ss"
                    ],
                'join': [", ", " and ", "\n"],
            }


def build_phrase(facet, entities, pattern, start):
    '''
    Function to build a sentence using data from the pre-defined templates
    '''
    if len(entities) > 1:
        if len(entities) == 2:
            conjunction = TEMPLATES['join'][1]
        else:
            conjunction = TEMPLATES['join'][0]
        entities_string = conjunction.join(entities)
        sentence = TEMPLATES['multiple'][pattern] % (facet, entities_string)
        # sentence = TEMPLATES['multiple'][0] % (facet, TEMPLATES['join'][0].join(entities))
    else:
        sentence = TEMPLATES['single'][0] % (entities[0], facet)
    # only the 1st sentence
    if pattern == 0:
        sentence = start + sentence
    return sentence


def test_rank_nodes(topn=20):
    ranking = rank_nodes(top_keywords)
    for i in range(topn):
        print ranking.get()


class DialogAgent():
    '''
    Chatbot talking data optimizing for knowledge transfer
    '''

    def __init__(self, top_keywords=top_keywords, index=INDEX):
        # establish connection to the
        self.db = ESClient(index)
        # keep track of the last transmitted node attribute to save space in the bucket
        self.top_keywords = top_keywords
        # normalization constant for estimating the total information space size
        self.space_size = 10140
        self.basket_limit = 5
        self.conversation_history = []
        # transition probabilities of replies to user intents with system actions
        self.intent2action = {
                'greeting': ['greeting', self.describe_set]
            }
        # initialize story stats
        self.transmitted_node = []
        self.transmitted_symbols = 0
        self.sum_weight = 0
        self.transmitted_messages = 0

    def chat(self, greeting="Hi, nice to meet you!", simulate=True):
        # 1. show default greeting
        if greeting:
            print 'S:', greeting
        self.conversation_history.append('greeting')

        # 2. users turn
        if simulate:
            user_message = "Hi!"
            print 'U:', user_message
        else:
            user_message = raw_input()
        
        # 3. match user input to all possible intents
        for intent in intents:
            if match_intent(user_message, intent):
                # pick the 1st matching system action
                for action in self.intent2action[intent]:
                    if action not in self.conversation_history:
                        if action not in actions.keys():
                            action()
                        else:
                            print 'S:', actions[action][0]

        # 4. users turn
        while True:
            if simulate:
                user_message = "I would like to know more about finanzen"
                print 'U:', user_message
            else:
                user_message = raw_input()
            
            # 5. search
            self.search_db(user_message)

    def search_db(self, query):
        stats = self.db.describe_subset(query)
        self.describe_set(keywords=stats, k=1, message="There are many datasets with related ",
                          query=query, show_sample=True)

    def report_message_stats(self):
        self.transmitted_messages += 1
        print "\t", self.sum_weight / self.transmitted_messages, "information units per message"
        print "\t", self.sum_weight / self.transmitted_symbols, "information units per symbol"
        print "\t%.2f of the information space communicated\n" % (self.sum_weight / float(self.space_size))

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

    def tell_facet(self, facet):
        '''
        show the first entities of the facet
        '''
        for entity in top_keywords[facet]['buckets'][:self.basket_limit]:
            self.communicate_node((-entity['doc_count'], (facet, entity['key'])))
            # print "\t", self.sum_weight / self.transmitted_symbols, "information units per symbol"
            # print "\t%.2f of the information space communicated\n" % (self.sum_weight / float(self.space_size))

    # def tell_facets(self, stats=all_keywords):
    #     # iterate over ranked facets
    #     facets_rank = gini_facets(stats)
    #     while not facets_rank.empty():
    #         weight, facet = facets_rank.get()
    #         self.tell_facet(facet)
    #         # report final message
    #         self.report_message_stats()
    
    def describe_set(self, query=None, k=2, keywords=all_keywords, threshold=0.02, show_sample=False,
                        message="In this Open Data portal there are many datasets with "):
        '''
        pick k facets from the gini index-based ranking queue
        '''
        # iterate over ranked facets
        facets_rank = gini_facets(keywords)
        for i in range(k):
            weight, facet = facets_rank.get()

            # for entity in keywords[facet]['buckets'][:self.basket_limit]:
                # self.communicate_node((-entity['doc_count'], (facet, entity['key'])))
            entities = []
            for entity in keywords[facet]['buckets'][:self.basket_limit]:
                x = entity['key']
                if entity['doc_count'] / float(N_DOCS) > threshold:
                    # filter out similar entities
                    duplicate_detected = False
                    for reported in entities:
                        # Edit distance of largest common substring (scaled)
                        partial = fuzz.partial_ratio(reported, x)
                        # print reported, x, partial
                        if partial == 100:
                            duplicate_detected = True
                            continue
                    if not duplicate_detected:
                        # print x, entity['doc_count']/float(N_DOCS)
                        entities.append(x)
            if entities:
                print 'S:', build_phrase(facet, entities, i, message)

                if show_sample:
                    # show sample datasets
                    for top_entity in entities:
                        items = self.db.sample_subset(keywords=query, facet_in=facet, entity=top_entity, limit=5)
                        examples = []
                        for item in items:
                            examples.append(item["_source"]['raw']['title'])
                    print 'S: For example:\n', TEMPLATES['join'][2].join(examples)
            else:
                print 'S:', actions['bool_data']['empty_set']

            

    def list_keywords(self, k=1, keywords=all_keywords, message="In this Open Data portal there are many datasets with "):
        '''
        pick k facets from the gini index-based ranking queue
        '''
        # iterate over ranked facets
        facets_rank = gini_facets(keywords)
        for i in range(k):
            weight, facet = facets_rank.get()
            # for entity in keywords[facet]['buckets'][:self.basket_limit]:
                # self.communicate_node((-entity['doc_count'], (facet, entity['key'])))
            entities = [entity['key'] for entity in keywords[facet]['buckets'][:self.basket_limit]]
            print 'S:', build_phrase(facet, entities, i, message)

    def list_keywords_greedy(self, k=2):
        '''
        pick k nodes from the ranking queue using greedy approach
        '''
        self.ranking = rank_nodes(self.top_keywords)
        for i in range(k):
            weight, relation = self.ranking.get()
            facet, entity = relation
            print 'S:', build_phrase(facet,[entity])

    def tell_story(self, topn=20):
        '''
        Runs the simulation of the knowledge flow
        simultaneously evaluating its productivity (velocity of the chanel)

        topn <int> defines the size of the story requested in terms of the number of concepts communicated
        '''
        self.tell_clusters(topn)

        # report final message
        self.report_message_stats()

        # report story stats
        print "\nTotal: communicated", self.sum_weight, "information units via", self.transmitted_symbols, "symbols in", self.transmitted_messages, "messages"
        print "\t%.2f of the information space covered" % (self.sum_weight / float(self.space_size))

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
            for node in clusters[facet][:self.basket_limit]:
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
        print build_phrase(facet, entities)


def test_sample_items():
    sample_items(attribute="raw.license_id.keyword", entity="cc-by-at-30", size=5)


def test_story_teller():
    story_size = 20  # n_concepts
    chatbot = DialogAgent()
    chatbot.tell_story(story_size)


def test_sample_subset(index=INDEX, top_n=1, limit=3, threshold=0.02):
    db = ESClient(index)
    query = "I would like to know more about finanzen"
    stats = db.describe_subset(query)
    # pick the most populated attributes
    facets_rank = gini_facets(stats)
    for k in range(top_n):
        # get the top facets
        weight, facet = facets_rank.get()
        print weight, facet
        # get the first bottom (last) facet by distribution
        # weight, facet_unique = facets_rank.reverse().get()

        # filter only most populated (important) entities based on ['doc_count'] values
        entities = []
        for entity in stats[facet]['buckets'][:limit]:
            x = entity['key']
            if entity['doc_count']/float(N_DOCS) > threshold:
                # filter out similar entities
                duplicate_detected = False
                for reported in entities:
                    # Edit distance of largest common substring (scaled)
                    partial = fuzz.partial_ratio(reported, x)
                    # print reported, x, partial
                    if partial == 100:
                        duplicate_detected = True
                        continue
                if not duplicate_detected:
                    # print x, entity['doc_count']/float(N_DOCS)
                    entities.append(x)

        print facet, entities

        for top_entity in entities:
            items = db.sample_subset(keywords=query, facet_in=facet, entity=top_entity)
            for item in items:
                print item["_source"]['raw']['title']


def test_gini_index():
    facets_rank = gini_facets(all_keywords)
    while not facets_rank.empty():
        # weight, facet
        print facets_rank.get()


def test_chat():
    chatbot = DialogAgent()
    chatbot.chat(greeting="Welcome, I will show you around data.gv.at", simulate=False)


def test_gini():
    # high inequality
    a = np.zeros((1000))
    a[0] = 1.0
    assert gini(a) > 0.99
    # uniform
    s = np.random.uniform(-1,0,1000)
    assert gini(s) > 0.32
    # equally homogeneous
    b = np.ones((1000))
    assert gini(b) == 0


def main():
    test_chat()


if __name__ == '__main__':
    main()
