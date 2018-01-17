'''
svakulenko
17 Jan 2017

Dialog agent for the conversational browsing task
'''

from load_ES import ESClient, INDEX


class DialogAgent():
    '''
    Dialog agent for the conversational browsing task
    '''

    def __init__(self, index=INDEX):
        # establish connection to the database
        self.db = ESClient(index)


def test_DialogAgent():
    chatbot = DialogAgent()


def main():
    test_DialogAgent()


if __name__ == '__main__':
    main()
