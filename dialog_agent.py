'''
svakulenko
17 Jan 2017

Dialog agent for the conversational browsing task
'''

from load_ES import ESClient, FACETS
from ranking import chunk_w_ranks, rank_chunks
from aggregations import facets, entities

class DialogAgent():
    '''
    Dialog agent for the conversational browsing task
    '''

    def __init__(self, l=4, simulation=False, search_only=False):
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
        self.search_only = search_only
        self.n = 0
        self.page = 0

    def restart(self):
        # reset goal to the whole information space
        self.goal = []
        self.history = []
        return self.chat(start=True)

    def reset_exploration(self, action='Continue', message=""):
        # No other datasets found!<br>
        # reset goal to the whole information space
        # if action == 'Continue':
        # remove last action
        # print 'goal', self.goal
        if self.goal:
            self.goal.pop()
        else:
            message += "No matching datasets found<br><br>"
        # print 'goal', self.goal
        # else:
        #     self.goal = []
            # self.history = []
        return self.chat(message=message, start=True)

    def clean(self, string, escape_chars=['[',']','{','}']):
        string = string.replace('-', ' ')
        return ''.join([char for char in string if char not in escape_chars])

    def search(self, action='Continue', message=''):
        # generate requests for different facets
        # if keywords:
        datasets = []
        all_concepts = []
        if action != 'Continue':
            self.goal = [('_search', action)]
            self.page = 0
            keywords = self.goal[0][1]
            for facet in FACETS.keys():
                result = self.db.summarize_subset(facets_values=[(facet, keywords)])
                n = result['hits']['total']
                if n > 0:
                    messages, all_concepts = self.show_titles(result['hits']['hits'], "Search", n)
                    datasets.extend(messages)
        #             message += "%d datasets for %s in %s<br>" % (n, keywords, facet)
        # return message, []
            if datasets:
                self.datasets = list(set(datasets))
                # print datasets
                self.n = len(self.datasets)
                message += "There are %d datasets" % self.n
            else:
                # reset goal
                if not self.search_only:
                    self.goal.pop()
                return "No matching datasets found", []
        if self.n <= self.page:
            # reset goal
            return "No matching datasets found", []
        next_page = self.page + self.l
        message += '<br>'.join(self.datasets[self.page:next_page])
        self.page = next_page
        # finish with the batch
        if self.n <= next_page and not self.search_only:
            # reset goal
            self.goal.pop()

        return message, []
        

    def aggregate_entities(self, result, message, n):
        aggregations = result['aggregations']
        # create chunks
        chunks = chunk_w_ranks(aggregations)
        # rank chunks
        chunks_rank = rank_chunks(chunks, self.l, self.history)
        entities = []
        # skip single entities as uninformative
        while len(entities) < 2:
            facet, entities = chunks_rank.get()[1]
            if not entities:
                return None, []
        if self.simulation:
            message += "There are %d datasets.\nYou can explore them by %s:\n\n%s" % (n, facet, '\n'.join(entities))
        else:
            # web-based chat html
            buttons = '<br>'.join(self.entity_decorator % (facet, entity, self.clean(entity)) for entity in entities)
            # if start or action != 'Continue':
            message += "There are %d datasets" % n
            if self.goal:
                message += " for %s" % ' and '.join(["%s: %s" % (goal_facet, self.clean(goal_entity)) for goal_facet, goal_entity in self.goal])
            else:
                message += " in total."
            message += "<br><br>You can explore them by "
            # else:
                # message += "<br>"
            message += "%s:<br>%s" % (facet, buttons)
            # add continue button
            # message += '''<br><br><button class='item' onclick="continueExploration()">Continue</button>'''
            # message += '''<br><button class='item' onclick="restart()">Restart</button>'''
        concepts = [(facet, entity) for entity in entities]
        self.history.extend(concepts)
        return message.encode('utf8'), concepts

    def show_titles(self, results, action, n):
        all_concepts = []
        messages = []
        # n_concepts = 0
        # if not self.simulation and action != 'Continue' and n > 1:
        #     message += "There are %d datasets" % n
        #     if self.goal:
        #         message += " for %s<br><br>" % ' and '.join(["%s: %s" % (goal_facet, self.clean(goal_entity)) for goal_facet, goal_entity in self.goal])
        for doc in results:
            message = ""
            # show all entities of the item
            concepts = self.db.compile_item_entities(doc['_source'])
            all_concepts.extend(concepts)
            if self.simulation:
                # show all entities that belong to the item
                message += "\n" + '\n'.join(["%s: %s" % (facet, entity) for facet, entity in concepts if (facet, entity) not in self.history])
                # n_new += 1
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

                
                # show only titles
                # for facet, entity in concepts:
                #     if facet == 'title':
                #         message += '<br>' + self.item_decorator % (dataset_link, entity)

                # show all entities that belong to the item
                for facet, entity in concepts:
                    
                    # if facet == 'title' or (facet, entity) not in self.history:
                    # if facet == 'title' or (facet, entity) not in self.history:
                        
                    # break on reaching the cognitive limit
                    # if n_concepts > self.l:
                    #     # self.history.extend(communicated_concepts)
                    #     return datasets, all_concepts
                    if facet == 'title':
                        # if (facet, entity) not in self.history:
                        message += "<br>%s: %s" % (facet, self.item_decorator % (dataset_link, self.clean(entity)))
                            # n_concepts += 1
                        # else:
                        #     break
                        # dataset.append((facet, entity))
                    # elif cognitive_resource > 0:
                    #     button = self.entity_decorator % (facet, entity, self.clean(entity))
                    #     message += '<br>' + "%s: %s" % (facet, button)
                    elif facet != 'tags':
                        message += '<br>' + "%s: %s" % (facet, self.clean(entity))
                        # dataset.append((facet, entity))
                        #     cognitive_resource -= 1
                        #     n_concepts += 1

                # add spacing between dataset descriptions
                # message += "<br>"
            if message:
                messages.append(message)
        # self.history.extend(communicated_concepts)
        return messages, all_concepts

    def chat(self, action='Continue', message="", start=False):
        # print action
        if action != 'Continue':
            # default exploration direction corresponds to the whole information space
            self.goal.append(action)
        # print 'Focus:', self.goal
        # get subset of the information space
        # if action[0] == '_search':
            # overwrite
            # self.goal = [action]

        # continue previous search results exploration
        for facet, value in self.goal:
            if facet == '_search':
                return self.search(action)

        result = self.db.summarize_subset(facets_values=self.goal)
        n = result['hits']['total']

        # form message
        if 'aggregations' in result.keys() and n > self.l:
            message, concepts = self.aggregate_entities(result, message, n)
            if not message:
                return self.reset_exploration()
            return message, concepts
        # show titles
        elif n > 0:
            messages, all_concepts = self.show_titles(result['hits']['hits'], action, n)
            
                # add continue button
                # message += '''<br><br><button class='item' onclick="continueExploration()">''' + action + '''</button>'''
                # message += '''<br><button class='item' onclick="restart()">Restart</button>'''
            # finish with the batch
            if n <= self.l:
                self.goal.pop()
            return "<br>".join(messages), all_concepts
            # else:
                # return self.reset_exploration(action)
                # message += "<br>No other datasets found"
                # if self.goal:
                #         message += " for %s" % ' and '.join(["%s: %s" % (goal_facet, self.clean(goal_entity)) for goal_facet, goal_entity in self.goal])
                # add continue button
                
                # reset goal to the whole information space
                # self.goal = []
                # return message, []
                # return self.reset_exploration()
        else:
            return self.reset_exploration()
            # message += "No matching datasets found"
            # # add continue button
            # message += '''<br><br><button class='item' onclick="continueExploration()">Continue</button>'''
            # return message, []


def test_DialogAgent():
    chatbot = DialogAgent()
    chatbot.chat()


def main():
    test_DialogAgent()


if __name__ == '__main__':
    main()
