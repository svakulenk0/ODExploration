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
        # model user knowledge
        self.memory = set()
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
        doc = self.db.get_random_doc()

        self.goal = set(self.db.compile_item_entities(doc))
        # self.goal = random.choice(items)

    def reply_random(self, actions):
        # check set intersect with the goal
        # print self.goal
        # print actions
        action_set = set(actions)
        # model perception mechanism
        self.memory = self.memory.union(action_set)
        # print self.memory

        # check success criteria, i.e. if we reached the goal
        # print "The user is looking for:", self.goal.difference(self.memory)
        if self.goal.issubset(self.memory):
            return 'Thank you!'

        match = action_set.intersection(self.goal)
        if not action_set.intersection(self.goal):
            # the goal is not reached yet, continue exploration
            # action = random.choice(actions)
            return 'Continue'
        else:
            return list(match)[0]



def test_define_random_goal():
    '''
    check a random item is assigned as a goal the simulated user gets
    '''
    user = Seeker()
    print user.goal


def simulate(l):
    '''
    Simulate conversation between a user and a dialog agent
    '''
    # initialize conversation partners
    user = Seeker()
    chatbot = DialogAgent(l)
    # start the conversation
    # show default greeting
    print 'A:', chatbot.greeting
    # start exploration
    message, actions = chatbot.chat()
    print message

    # count number of turns
    n_turns = 1
    while True:
        # choose exploration direction
        if actions:
            action = user.chat(actions)
            if isinstance(action, tuple):
                message = action[1]
            else:
                message = action
            print '\nU:%s\n' % message
            # success-stopping condition
            if action == 'Thank you!':
                break
        # continue exploration
        message, actions = chatbot.chat(action)
        print 'A:', message
        n_turns += 1

    return n_turns


def run_evaluation(l=8, k=500):
    '''
    Run simulation n times:

    k <int> number of runs
    '''
    n_turns = []
    for i in range(k):
        n_turns.append(simulate(l))

    # show stats
    print "Cognitive resource:", l
    print "\nDistribution of the number of turns per dialog (%d runs):" % k
    print sorted(n_turns)
    print "Minimum number of turns per dialog", min(n_turns)
    print "Average number of turns per dialog", reduce(lambda x, y: x + y, n_turns) / len(n_turns)
    print "Maximum number of turns per dialog", max(n_turns)


def evaluate_sensitivity():
    for l in [3, 4, 5, 6, 7, 8]:
        run_evaluation(l)


if __name__ == '__main__':
    run_evaluation()
