'''
svakulenko
25 Dec 2017

Dialog agent class
'''
from Queue import PriorityQueue

from load_ES import ESClient, INDEX
from aggregations import all_keywords


class DialogAgent():
    '''
    Chatbot implementing get_response method
    '''

    def __init__(self, index=INDEX):
        # establish connection to the ES index
        self.db = ESClient(index)
        # initialize the rank for entity facet pairs by count from db
        self.rank_entities()

    def rank_entities(self, entity_counts=all_keywords):
        '''
        rank entities with facets from ES index by the item count
        '''
        # initialize a priority queue to store nodes ranking
        self.entity_rank = PriorityQueue()
        #  iterate over attributes
        for facet, counts in entity_counts.items():
            entities = counts['buckets']
            # iterate over top entities of the attribute
            for entity in entities:
                # insert into the priority queue (max weight items to go first)
                self.entity_rank.put((-entity['doc_count'], (facet, entity['key'])))

    def sample_items(self, facet, entity, size):
        '''
        show a sample of items for an entity
        '''
        samples = []
        results = self.db.search_by(facet=facet, value=entity, limit=size)
        for item in results:
            samples.append(item["_source"]["raw"]["title"])
        return "\nFor example:\n\n" + "\n".join(samples)

    def tell_story(self):
        response = ""
        count, (facet, entity) = self.entity_rank.get()
        response += "There are %s datasets with %s as %s\n" % (-count, entity, facet)
        # show examples TODO
        response += self.sample_items(facet, entity, size=5)
        return response

    def get_response(self, user_request):
        return self.tell_story()


def test_rank_nodes(topn=5):
    chatbot = DialogAgent()
    chatbot.rank_entities()
    for i in range(topn):
        print chatbot.entity_rank.get()


def test_get_response(n_turns=5):
    chatbot = DialogAgent()
    for i in range(n_turns):
        user_message = "ok"
        # user says
        print user_message
        # bot says
        print chatbot.get_response(user_message)


if __name__ == '__main__':
    test_get_response()
