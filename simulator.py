'''
svakulenko
3 Jan 2017

User simulator to evaluate dialog agent interaction performance.
'''
from dialog_agent import DialogAgent
from load_ES import ESClient, INDEX_LOCAL


def test_BFS(index=INDEX_LOCAL, n_turns=15):
    '''
    Default search strategy is breadth-first exploring all important facets
    '''
    chatbot = DialogAgent(index, spacing='\n')
    for i in range(n_turns):
        user_message = "ok"
        # user says
        print user_message
        # bot says
        print chatbot.get_response(user_message)
        print '\n'


if __name__ == '__main__':
    test_BFS()
