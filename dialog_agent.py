'''
svakulenko
17 Jan 2017

Dialog agent for the conversational browsing task
'''

from load_ES import ESClient
from ranking import chunk_w_ranks, rank_chunks
from aggregations import facets, entities

class DialogAgent():
    '''
    Dialog agent for the conversational browsing task
    '''

    def __init__(self, l=8):
        # establish connection to the database
        self.db = ESClient()
        # concepts already communicated to the user
        self.history = []
        # ranking of concept chunks from the database
        self.rank = []
        # default greeting message
        self.greeting = "Hi! Welcome to the Austrian Open Data portal!"
        # maximum message size
        self.l = l
        # default exploration direction corresponds to the whole information space
        self.goal = []

    def chat(self, action='Continue'):
        # print action
        if action != 'Continue':
            # default exploration direction corresponds to the whole information space
            self.goal.append(action)
        # print 'Focus:', self.goal
        # get subset of the information space
        result = self.db.summarize_subset(facets_values=self.goal)
        n = result['hits']['total']

        # form message
        if 'aggregations' in result.keys() and n > 1:
            entities = result['aggregations']
            # create chunks
            chunks = chunk_w_ranks(entities)
            # rank chunks
            chunks_rank = rank_chunks(chunks, self.l, self.history)
            facet, entities = chunks_rank.get()[1]
            message = "There are %d datasets.\nYou can explore them by %s:\n\n%s" % (n, facet, '\n'.join(entities))
            concepts = [(facet, entity) for entity in entities]
            self.history.extend(concepts)
            return message, concepts
        # found it
        elif n > 0:
            message = "Here you are:"
            concepts = []
            for i, doc in enumerate(result['hits']['hits']):
                # show all entities of the item
                concepts.extend(self.db.compile_item_entities(doc['_source']))
                message += "\n%s. Dataset\n\n%s" % (i+1, '\n'.join(["%s: %s" % (facet, entity) for facet, entity in concepts]))
            return message, concepts
        else:
            return "No matching datasets found", []


def test_DialogAgent():
    chatbot = DialogAgent()
    chatbot.chat()


def main():
    test_DialogAgent()


if __name__ == '__main__':
    main()
