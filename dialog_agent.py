'''
svakulenko
25 Dec 2017

Dialog agent class
'''
from Queue import PriorityQueue

from load_ES import ESClient, INDEX, INDEX_CSV
from aggregations import all_keywords


class DialogAgent():
    '''
    Chatbot implementing get_response method
    '''

    def __init__(self, sample=True, spacing='<br>'):
        # establish connection to the ES index
        self.db = ESClient(INDEX)
        self.csv_db = ESClient(INDEX_CSV, host='csvengine', port=9201)
        # initialize a priority queue to store nodes ranking
        self.entity_rank = PriorityQueue()
        self.spacing = spacing
        self.title_decorator = "<a class='item'>%s</a>"

    def rank_entities(self, entity_counts=all_keywords):
        '''
        rank entities with facets from ES index by the item count
        '''
        #  iterate over attributes
        for facet, counts in entity_counts.items():
            entities = counts['buckets']
            # iterate over top entities of the attribute
            for entity in entities:
                # insert into the priority queue (max weight items to go first)
                self.entity_rank.put((-entity['doc_count'], (facet, entity['key'])))

    def sample_items(self, size):
        '''
        show a sample of items for an entity
        '''
        samples = []
        for item in self.items[self.page:self.page+size]:
            # get title
            title = item["_source"]["raw"]["title"]
            # get the set of formats
            formats = set([resource['format'] for resource in item["_source"]["raw"]["resources"]])
            if 'CSV' in formats:
                # get table
                dataset_id = item["_source"]["raw"]["id"]
                dataset_link = "http://www.data.gv.at/katalog/dataset/%s" % dataset_id
                self.csv_db.search_by(facet='dataset_link', value=dataset_link)
                # get columns
            # self.shown.add(title)
            samples.append(self.title_decorator % title)
        self.page += size
        return self.spacing.join(samples)

    def tell_story(self):
        response = ""
        if self.entity_rank.empty():
            # reset initialize the rank for entity facet pairs by count from db
            self.rank_entities()
            # reset already shown items
            self.shown = set()
        count, (facet, entity) = self.entity_rank.get()
        response += "There are %s datasets with %s as %s%s" % (-count, entity, facet, self.spacing)
        # show examples
        self.items = self.db.search_by(facet=facet, value=entity)
        # show only new items
        # self.items = list(set([item["_source"]["raw"]["title"] for item in items]) - self.shown)
        if self.items:
            self.page = 0
            sampled_titles = self.sample_items(size=5)
            response += "%sFor example:%s" % (self.spacing, self.spacing*2) + sampled_titles
            return response
        else:
            # try another entity
            return self.tell_story()

    def get_response(self, user_request):
        return self.tell_story()


def test_rank_nodes(topn=5):
    chatbot = DialogAgent()
    chatbot.rank_entities()
    for i in range(topn):
        print chatbot.entity_rank.get()


def test_get_response(n_turns=5):
    chatbot = DialogAgent(spacing='\n')
    for i in range(n_turns):
        user_message = "ok"
        # user says
        print user_message
        # bot says
        print chatbot.get_response(user_message)
        print '\n'

        # get all items for this entity DFS
        if chatbot.page < len(chatbot.items):
            # user says
            print "more"
            # get more samples
            # bot says
            print chatbot.sample_items(size=10)
            print '\n'


if __name__ == '__main__':
    test_get_response()
