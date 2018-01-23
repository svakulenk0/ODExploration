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

    def __init__(self, l=8, simulation=False):
        # establish connection to the database
        self.db = ESClient()
        # concepts already communicated to the user
        self.history = []
        # ranking of concept chunks from the database
        self.rank = []
        # default greeting message
        self.greeting = "Hi! Welcome to the Austrian Open Data portal!"
        self.entity_decorator = '''<button class='item' onclick="pivotEntity('%s','%s')">%s</button>'''
        # maximum message size
        self.l = l
        # default exploration direction corresponds to the whole information space
        self.goal = []
        # message formatting HTML vs text
        self.simulation = simulation

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
        if 'aggregations' in result.keys() and n > self.l:
            entities = result['aggregations']
            # create chunks
            chunks = chunk_w_ranks(entities)
            # rank chunks
            chunks_rank = rank_chunks(chunks, self.l, self.history)
            facet, entities = chunks_rank.get()[1]
            if self.simulation:
                message = "\nThere are %d datasets.\nYou can explore them by %s, e.g.:\n\n%s" % (n, facet, '\n'.join(entities))
            else:
                # web-based chat html
                buttons = '<br>'.join(self.entity_decorator % (facet, entity, entity) for entity in entities)
                message = "<br>There are %d datasets.<br>You can explore them by %s, e.g.:<br><br>%s" % (n, facet, buttons)
            concepts = [(facet, entity) for entity in entities]
            self.history.extend(concepts)
            return message.encode('utf8'), concepts
        # found it
        elif n > 0:
            message = "<br>Here you are:"
            concepts = []
            for i, doc in enumerate(result['hits']['hits']):
                # show all entities of the item
                concepts.extend(self.db.compile_item_entities(doc['_source']))
                if self.simulation:
                    message += "\n\n" + '\n'.join(["%s: %s" % (facet, entity) for facet, entity in concepts])
                else:
                # web-based chat html
                    message += "<br><br>" + '<br>'.join(["%s: %s" % (facet, entity) for facet, entity in concepts])
            return message.encode('utf8'), concepts
        else:
            # reset goal to the whole information space
            self.goal = []
            self.history = []
            return "No matching datasets found", []


def test_DialogAgent():
    chatbot = DialogAgent()
    chatbot.chat()


def main():
    test_DialogAgent()


if __name__ == '__main__':
    main()
