'''
svakulenko
17 Jan 2017

Dialog agent for the conversational browsing task
'''

from load_ES import ESClient, INDEX
from ranking import chunk_w_ranks, rank_chunks
from aggregations import facets, entities

class DialogAgent():
    '''
    Dialog agent for the conversational browsing task
    '''

    def __init__(self, index=INDEX):
        # establish connection to the database
        self.db = ESClient(index)
        # concepts already communicated to the user
        self.history = []
        # ranking of concept chunks from the database
        self.rank = []
        # default greeting message
        self.greeting = "Hi! Welcome to the Austrian Open Data portal!"
        # maximum message size
        self.l = 4

    def chat(self, action=None):
        # get subset of the information model, {} corresponds to the whole information space
        entities, n = self.db.summarize_subset(facets_values=action)
        # form message
        if n > 0:
            # create chunks
            chunks = chunk_w_ranks(entities)
            # rank chunks
            chunks_rank = rank_chunks(chunks, self.l, self.history)
            facet, concepts = chunks_rank.get()[1]
            message = "There are %d datasets with %s: %s" % (n, facet, ', '.join(concepts))
            # show message
            # print 'A:', message
            self.history.extend(concepts)
            actions = [{facet: concept} for concept in concepts]
            return message, actions
        else:
            return "No matching datasets found", {}

            # 4. users turn
            # if simulate:
            #     user_message = "Hi!"
            #     print 'U:', user_message
            # else:
            #     user_message = raw_input()


def test_DialogAgent():
    chatbot = DialogAgent()
    chatbot.chat()


def main():
    test_DialogAgent()


if __name__ == '__main__':
    main()
