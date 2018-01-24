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

    def __init__(self, l=5, simulation=False):
        # establish connection to the database
        self.db = ESClient()
        # concepts already communicated to the user
        self.history = []
        # ranking of concept chunks from the database
        self.rank = []
        # default greeting message
        self.greeting = "Hi! Welcome to the Austrian Open Data portal!"
        # web-based chat buttons and links html
        self.entity_decorator = '''<button class='item' onclick="pivotEntity('%s','%s')">%s</button>'''
        self.item_decorator = "<a href='%s'>%s</a>"
        # maximum message size
        self.l = l
        # default exploration direction corresponds to the whole information space
        self.goal = []
        # message formatting HTML vs text
        self.simulation = simulation

    def reset_exploration(self, action='Continue'):
        # reset goal to the whole information space
        self.goal = []
        # self.history = []
        return self.chat(action)

    def clean(self, string, escape_chars=['[',']','{','}']):
        string = string.replace('-', ' ')
        return ''.join([char for char in string if char not in escape_chars])

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
            if entities:
                if self.simulation:
                    message = "There are %d datasets.\nYou can explore them by %s:\n\n%s" % (n, facet, '\n'.join(entities))
                else:
                    # web-based chat html
                    buttons = '<br>'.join(self.entity_decorator % (facet, entity, self.clean(entity)) for entity in entities)
                    message = "<br>There are %d datasets" % n
                    if self.goal:
                        message += " for %s" % ', '.join(["%s: %s" % (goal_facet, self.clean(goal_entity)) for goal_facet, goal_entity in self.goal])
                    else:
                        message += " in total."
                    message += "<br>You can explore them by %s:<br><br>%s" % (facet, buttons)
                    # add continue button
                    message += '''<br><br><button class='item' onclick="continueExploration()">Continue</button>'''
                concepts = [(facet, entity) for entity in entities]
                self.history.extend(concepts)
                return message.encode('utf8'), concepts
            else:
                return self.reset_exploration(action)
        # found it
        elif n > 0:
            # if self.simulation:
            #     message = "Here you are:"
            # else:
            #     message = "<br>Here you are:"
            message = ''
            all_concepts = []
            n_new = 0
            # communicated_concepts = []
            for doc in result['hits']['hits'][:self.l]:
                # show all entities of the item
                concepts = self.db.compile_item_entities(doc['_source'])
                all_concepts.extend(concepts)
                if self.simulation:
                    # show all entities that belong to the item
                    message += "\n" + '\n'.join(["%s: %s" % (facet, entity) for facet, entity in concepts if (facet, entity) not in self.history])
                    n_new += 1
                    # show only titles
                    # for facet, entity in concepts:
                    #     if facet == 'title':
                    #         message += '\n' +  entity
                            # communicated_concepts.append((facet, entity))
                else:
                    # web-based chat html
                    # get link to the dataset
                    dataset_id = doc["_source"]["raw"]["id"]
                    dataset_link = "http://www.data.gv.at/katalog/dataset/%s" % dataset_id

                    # add spacing between dataset descriptions
                    message += "<br>"
                    
                    # show only titles
                    # for facet, entity in concepts:
                    #     if facet == 'title':
                    #         message += '<br>' + self.item_decorator % (dataset_link, entity)

                    # show all entities that belong to the item
                    for facet, entity in concepts:
                        if facet == 'title':
                            message += '<br>' + "%s: %s" % (facet, self.item_decorator % (dataset_link, self.clean(entity)))
                        elif (facet, entity) not in self.history:
                            button = self.entity_decorator % (facet, entity, self.clean(entity))
                            message += '<br>' + "%s: %s" % (facet, button)
                            n_new += 1

                    # add continue button
                    message += '''<br><br><button class='item' onclick="continueExploration()">Continue</button>'''
            self.history.extend(all_concepts)
            if n_new > 0:
                return message.encode('utf8'), all_concepts
            else:
                return self.reset_exploration()
        else:
            return self.reset_exploration(action)
            # return "No matching datasets found", []


def test_DialogAgent():
    chatbot = DialogAgent()
    chatbot.chat()


def main():
    test_DialogAgent()


if __name__ == '__main__':
    main()
