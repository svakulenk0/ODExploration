'''
svakulenko
25 Dec 2017

Dialog agent class
'''
from Queue import PriorityQueue

from load_ES import ESClient, INDEX_LOCAL, INDEX_SERVER, INDEX_CSV
from aggregations import all_keywords


class DialogAgent():
    '''
    Chatbot implementing get_response method
    '''

    def __init__(self, index=INDEX_LOCAL, sample=True, spacing='<br>'):
        # establish connection to the ES index
        self.db = ESClient(index)
        self.start = True
        self.csv_db = ESClient(INDEX_CSV, host='csvengine', port=9201)
        # initialize a priority queue to store nodes ranking
        self.entity_rank = PriorityQueue()
        self.spacing = spacing
        self.title_decorator = "<button class='item' onclick=showDataset('%s')>%s</button>"
        self.link_decorator = "<a href='%s'>%s</a>"

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

    def show_dataset(self, dataset_id):
        entities = []
        items = self.db.search_by(facet='dataset_id', value=dataset_id)
        if items:
            title = items[0]["_source"]["raw"]["title"]
            dataset_link = "http://www.data.gv.at/katalog/dataset/%s" % dataset_id
            entities.append(self.link_decorator % (dataset_link, title))
            # get the set of formats
            formats = set([resource['format'] for resource in item["_source"]["raw"]["resources"]])
            entities.extend(formats)
            
            if 'CSV' in formats:
                # get table
                tables = self.csv_db.search_by(facet='dataset_link', value=dataset_link)
                if tables:
                    table = tables[0]['_source']
                    if 'no_rows' in table.keys():
                        facet = 'no_rows'
                        entities.append('%s: %s' % (facet, table[facet]))
            
            return self.spacing + self.spacing.join(entities)

    def sample_items(self, size):
        '''
        show a sample of items for an entity
        '''
        samples = []
        for item in self.items[self.page:self.page+size]:
            # get title
            title = item["_source"]["raw"]["title"]
            dataset_id = item["_source"]["raw"]["id"]
            # self.shown.add(title)
            samples.append(self.title_decorator % (dataset_id, title))
        self.page += size
        return self.spacing.join(samples)

    def show_facets(self, entity_counts=all_keywords):
        facets = []
        for facet, counts in entity_counts.items():
            facets.append(facet)
        self.start = False
        return self.spacing.join(facets)

    def show_top_entities(self):
        response = ""
        if self.entity_rank.empty():
            # reset initialize the rank for entity facet pairs by count from db
            self.rank_entities()
            # reset already shown items
            self.shown = set()
        count, (facet, entity) = self.entity_rank.get()
        response += "%sThere are %s datasets with %s as %s%s" % (self.spacing, -count, entity, facet, self.spacing)
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
            return self.show_top_entities()

    def tell_story(self):
        # if self.start:
        #     return self.show_facets()
        # else:
        return self.show_top_entities()

    def get_response(self, user_request):
        return self.tell_story()


def test_rank_nodes(topn=5):
    chatbot = DialogAgent()
    chatbot.rank_entities()
    for i in range(topn):
        print chatbot.entity_rank.get()


def test_get_response(index=INDEX_SERVER, n_turns=5):
    chatbot = DialogAgent(index, spacing='\n')
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


def test_get_CSV(index=INDEX_SERVER):
    chatbot = DialogAgent(index, spacing='\n')
    dataset_id = '94c1d9b8-4e57-4e51-a22c-3681de46b723'
    print chatbot.show_dataset(dataset_id)


if __name__ == '__main__':
    test_get_response()
