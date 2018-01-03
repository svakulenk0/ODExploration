'''
svakulenko
3 Jan 2017

User simulator class to evaluate dialog agent interaction performance.
'''
from dialog_agent import DialogAgent
from load_ES import ESClient, INDEX_LOCAL


class Seeker():
    '''
    '''
    def __init__(self, time, strategy):
        # number of dialogue turns, time T
        self.time = time
        if strategy == 'bfs':
            self.reply = self.bfs
        elif strategy == 'dfs':
            self.reply = self.dfs

    def bfs(self):
        '''
        ask for diversity in results, horizontal search
        '''
        return "other"

    def dfs(self):
        '''
        vertical search, get exhaustive list of results
        '''
        return "more"


def test_BFS(index=INDEX_LOCAL):
    '''
    Default search strategy is breadth-first exploring all important facets
    '''
    chatbot = DialogAgent(index, spacing='\n')
    user = Seeker(time=5, strategy='bfs')
    for i in range(user.time):
        # user says
        user_message = user.reply()
        print user_message
        # bot says
        print chatbot.get_response(user_message)
        print '\n'


def test_DFS(index=INDEX_LOCAL, n_turns=15):
    '''
    Default search strategy is breadth-first exploring all important facets
    '''
    chatbot = DialogAgent(index, spacing='\n')
    user = Seeker(time=5, strategy='dfs')
    for i in range(user.time):
        # user says
        user_message = user.reply()
        print user_message
        # bot says
        print chatbot.get_response(user_message)
        print '\n'


if __name__ == '__main__':
    test_BFS()
