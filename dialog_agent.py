#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
svakulenko
17 Jan 2017

Dialog agent for the conversational browsing task
'''

from .load_ES import ESClient, FACETS, DATASET_LINK, N
from .ranking import chunk_w_ranks, rank_chunks
from .aggregations import facets, entities


TEMPLATES = {
        'en': {
            'greeting': "Welcome to the Austrian Open Data portal!",
            'not_found': "No matching datasets found",
            'n_datasets': "There are %d datasets\n\n",
            'many_datasets': "There are many datasets, e.g.:\n\n",
            # 'many_datasets': "There are many datasets about **%s** e.g.:\n\n",
            'explore': "\n\nYou can explore them by ",
            'total': " in total.",
            'goal': " for %s",
            'connector': " and ",
            },
        'de': {
            'greeting': "Willkommen am Oesterreichischen Open Data Portal!",
            # 'greeting': "Hi! Willkommen am österreichischen Open Data Portal!",
            'not_found': "Keine Datensaetze gefunden",
            # 'not_found': "Keine Datensätze gefunden",
            'n_datasets': "Hier gibt es %d Datensaetze zu entdecken!",
            # 'n_datasets': "Hier gibt es %d Datensätze zu entdecken",
            'explore': "<br><br>Du kannst Sie filtern per ",
            'total': " , insgesamt.",
            'goal': " fuer %s",
            # 'goal': " für %s",
            'connector': " und ",
            },
    }


class DialogAgent():
    '''
    Dialog agent for the conversational browsing task
    '''

    def __init__(self, l=6, simulation=False, search_only=False, lang='en'):
        # establish connection to the database
        self.db = ESClient()
        # concepts already communicated to the user
        self.history = []
        # ranking of concept chunks from the database
        self.rank = []
        self.lang = lang
        # default greeting message
        # self.greeting = TEMPLATES[self.lang]['greeting']
        # web-based chat buttons and links html
        # self.entity_decorator = '''<button class='item' onclick="pivotEntity('%s','%s')">%s</button>'''
        # self.entity_decorator = '''**%s**'''
        self.entity_decorator = '''%s'''
        # self.item_decorator = "<a href='%s'>%s</a>"
        self.item_decorator = "[%s](%s)"
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
            message += TEMPLATES[self.lang]['not_found'] + "<br><br>"
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
            words = keywords.split()
            print(words)
            # if len(words) > 0:
            result = self.db.search(keywords=' AND '.join(words))
            n = result['hits']['total']
            print('%d datasets found' % n)
            if n > 0:
                messages, all_concepts = self.show_titles(result['hits']['hits'], "Search", n)
                datasets.extend(messages)
            # else:
            #     for facet in FACETS.keys():
            #         result = self.db.summarize_subset(facets_values=[(facet, keywords)])
            #         n = result['hits']['total']
            #         if n > 0:
            #             messages, all_concepts = self.show_titles(result['hits']['hits'], "Search", n)
            #             datasets.extend(messages)
        #             message += "%d datasets for %s in %s<br>" % (n, keywords, facet)
        # return message, []
            if datasets:
                self.datasets = list(set(datasets))
                # print datasets
                self.n = len(self.datasets)
                # if self.n < N:
                #     # message += TEMPLATES[self.lang]['n_datasets'] % (self.n, ' about **%s** ' % keywords)
                #     message += TEMPLATES[self.lang]['n_datasets'] % (self.n)
                # else:
                #     # message += TEMPLATES[self.lang]['many_datasets'] % keywords
                #     message += TEMPLATES[self.lang]['many_datasets']
            else:
                # reset goal
                if not self.search_only:
                    self.goal.pop()
                return TEMPLATES[self.lang]['not_found'], []
        if self.n <= self.page:
            # reset goal
            return TEMPLATES[self.lang]['not_found'], []
        next_page = self.page + self.l
        message += '\n\n'.join(self.datasets[self.page:next_page])
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
        facet, entities = chunks_rank.get()[1]
        # entities = []
        # skip single entities as uninformative
        # while len(entities) < 2:
            # facet, entities = chunks_rank.get()[1]
        if not entities:
            return None, []
        if self.simulation:
            message += "There are %d datasets. * You can explore them by %s: * %s" % (n, facet, '*'.join(entities))
        else:
            # web-based chat html
            # buttons = '*'.join(self.entity_decorator % (facet, entity, self.clean(entity)) for entity in entities)
            buttons = '\n\n'.join(self.entity_decorator % self.clean(entity) for entity in entities)
            # if start or action != 'Continue':
            # message += TEMPLATES[self.lang]['n_datasets'] % (n, '')
            # message += TEMPLATES[self.lang]['n_datasets'] % n
            # if self.goal:
            #     message += TEMPLATES[self.lang]['goal'] % TEMPLATES[self.lang]['connector'].join(["%s: %s" % (goal_facet, self.clean(goal_entity)) for goal_facet, goal_entity in self.goal])
            # else:
            #     message += TEMPLATES[self.lang]['total']
            message += TEMPLATES[self.lang]['explore']
            # else:
                # message += "<br>"
            message += "%s:\n\n%s" % (facet, buttons)
            # add continue button
            # message += '''<br><br><button class='item' onclick="continueExploration()">Continue</button>'''
            # message += '''<br><button class='item' onclick="restart()">Restart</button>'''
        concepts = [(facet, entity) for entity in entities]
        self.history.extend(concepts)
        return message.encode('utf8'), concepts

    def show_titles(self, results, action, n):
        all_concepts = []
        messages = []
        # print results
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
                # print message
                # n_new += 1
                # show only titles
                # for facet, entity in concepts:
                #     if facet == 'title':
                #         message += '\n' +  entity
                        # communicated_concepts.append((facet, entity))
            else:
                # web-based chat html
                # get link to the dataset
                # dataset_id = doc["_source"]["raw"]["id"]
                # dataset_link = "http://www.data.gv.at/katalog/dataset/%s" % dataset_id
                # try:
                #     print (doc["_source"]['dataset']['dataset_link'])
                # except:
                #     print("except!")
                # print (doc["_source"])
                dataset_link = doc["_source"]['dataset']['dataset_link']
                # dataset_link = "hi"
                # print (dataset_link)
                # print (concepts)
                
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
                        # try:
                        # message += "<br>%s: %s" % (facet, self.item_decorator % (dataset_link, self.clean(entity)))
                        message += "\n\n%s" % (self.item_decorator % (self.clean(entity), dataset_link))

                highlights = doc["highlight.row.values.value"]
                for highlight in highlights:
                    message += "\n\n%s" % highlight

                        # message += "\n\n%s" % (self.clean(entity))
                        # message += "\n\n%s: %s" % (facet, self.clean(entity))
                # message += "\n\n%s" % doc['highlight']
                        # except:
                            # break
                            # n_concepts += 1
                        # else:
                        #     break
                        # dataset.append((facet, entity))
                    # elif cognitive_resource > 0:
                    #     
                    # elif facet != 'tags':
                    #     # attach buttons for item entities
                    #     # try:
                    #         # button = self.entity_decorator % (facet, entity, self.clean(entity))
                    #     button = self.entity_decorator % self.clean(entity)
                    #     message += '\n\n' + "%s: %s" % (facet, button)
                        # except:
                        #     break
                        # message += '<br>' + "%s: %s" % (facet, self.clean(entity))
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
        # for facet, value in self.goal:
        #     if facet == '_search':
        #         return self.search(action)

        result = self.db.summarize_subset(facets_values=self.goal)
        n = result['hits']['total']
        print(n, 'results')
        # print(result)
        # form message
        if 'aggregations' in result.keys() and n > self.l:
            message, concepts = self.aggregate_entities(result, message, n)
            if not message:
                return self.restart()
            return str(message, 'utf-8'), concepts
        # show titles
        elif n > 0:
            messages, all_concepts = self.show_titles(result['hits']['hits'], action, n)
            
                # add continue button
                # message += '''<br><br><button class='item' onclick="continueExploration()">''' + action + '''</button>'''
                # message += '''<br><button class='item' onclick="restart()">Restart</button>'''
            # finish with the batch
            if n <= self.l:
                self.goal.pop()
            return str("\n\n\n\n".join(messages), 'utf-8'), all_concepts
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
    print(chatbot.chat())


def main():
    test_DialogAgent()


if __name__ == '__main__':
    main()
