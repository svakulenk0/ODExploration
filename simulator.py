'''
svakulenko
17 Jan 2017

User simulator class to evaluate performance of the dialog agent
'''
import random

from aggregations import entities
from dialog_agent import DialogAgent

class Seeker():
    '''
    User simulator class
    '''
    def __init__(self):
        # cognitive resource limit
        self.l = 9
        # initialize goal to a random concept from the information model
        self.define_random_goal()
        # selection strategy of the agent with respect to the set of actions
        # offered by the agent
        self.chat = self.reply_random

    def define_random_goal(self):
        entities_list = [entity['key'] for facet in entities.values() for entity in facet['buckets']]
        self.goal = random.choice(entities_list)

    def reply_random(self, concepts):
        if self.goal not in concepts:
            # the goal is not reached yet, continue exploration
            action = random.choice(concepts)
            return action
        else:
            return 'Yes'


def test_define_random_goal():
    user = Seeker()
    print user.goal


def simulate(n=2):
    '''
    Simulate conversation between a user and a dialog agent
    n <int> number of turns
    '''
    # initialize conversation partners
    user = Seeker()
    chatbot = DialogAgent()
    action = {}
    # start the conversation
    # show default greeting
    print 'A:', chatbot.greeting
    for i in range(n):
        actions = chatbot.chat(action)
        print 'A:', actions
        action = user.chat(actions)
        print 'U:', action


if __name__ == '__main__':
    simulate()
