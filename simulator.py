'''
svakulenko
17 Jan 2017

User simulator class to evaluate performance of the dialog agent
'''
import random

from load_ES import ESClient
from aggregations import entities
from dialog_agent import DialogAgent

class Seeker():
    '''
    User simulator class
    '''
    def __init__(self):
        # establish connection to the database
        self.db = ESClient()
        # cognitive resource limit
        self.l = 9
        # initialize goal to a random concept from the information model
        self.define_goal()
        # selection strategy of the agent with respect to the set of actions
        # offered by the agent
        self.chat = self.reply_random

    def define_goal(self):
        # pick at item from the database at random
        # entities_list = [entity['key'] for facet in entities.values() for entity in facet['buckets']]
        self.goal = self.db.get_random_item()
        # self.goal = random.choice(items)

    def reply_random(self, actions):
        # check set intersect with the goal
        # print self.goal
        print actions
        # concepts = [concept for action.val]
        if not set(self.goal) & set(actions):
            # the goal is not reached yet, continue exploration
            action = random.choice(actions)
            return action
        else:
            return 'Yes'


def test_define_random_goal():
    '''
    check a random item is assigned as a goal the simulated user gets
    '''
    user = Seeker()
    print user.goal


def simulate(n=12):
    '''
    Simulate conversation between a user and a dialog agent
    n <int> number of turns
    '''
    # initialize conversation partners
    user = Seeker()
    chatbot = DialogAgent()
    action = None
    # start the conversation
    # show default greeting
    print 'A:', chatbot.greeting
    # start exploration
    message, actions = chatbot.chat(action)
    print 'A:', message
    for i in range(n):
        # choose exploration direction
        if actions:
            action = user.chat(actions)
            print 'U:', action
        # continue exploration
        message, actions = chatbot.chat(action)
        print 'A:', message


if __name__ == '__main__':
    simulate()
