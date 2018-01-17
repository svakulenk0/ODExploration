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

    def reply_random(self, actions):
        if self.goal not in actions:
            # the goal is not reached yet, continue exploration
            action = random.choice(actions)
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
