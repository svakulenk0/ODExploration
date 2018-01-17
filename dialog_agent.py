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
        # partition the whole information space into coherent chunks
        self.chunks = chunk_w_ranks(facets, entities)
        # concepts already communicated to the user
        self.history = []
        # ranking of concept chunks from the database
        self.rank = []
        # default greeting message
        self.greeting = "Hi! Welcome to the Austrian Open Data portal!"
        # maximum message size
        self.l = 4

    def chat(self, action={}):
        # get subset of the information model, {} corresponds to the whole information space
        # create chunks
        # chunk_w_ranks(facets, entities)

        # rank chunks
        chunks_rank = rank_chunks(self.chunks, self.l, self.history)
        concepts = chunks_rank.get()[1]
        # message = concepts
        # show message
        # print 'A:', message
        self.history.extend(concepts)
        return concepts

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
