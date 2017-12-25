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

    def __init__(self, index=INDEX_SERVER, sample=True, spacing='<br>'):
        # establish connection to the ES index
        self.db = ESClient(index)
        self.csv_db = ESClient(INDEX_CSV, host='csvengine', port=9201)
        # initialize a priority queue and store entity ranking
        self.entity_rank = self.rank_entities()
        self.spacing = spacing
        # self.title_decorator = "<button class='item' onclick=showDataset('%s')>%s</button>"
        self.item_decorator = "<a class='item' href='%s'>%s</a>%s"

    def rank_entities(self, entity_counts=all_keywords):
        '''
        rank entities with facets from ES index by the item count
        '''
        entity_rank = PriorityQueue()
        #  iterate over attributes
        for facet, counts in entity_counts.items():
            entities = counts['buckets']
            # iterate over top entities of the attribute
            for entity in entities:
                # insert into the priority queue (max weight items to go first)
                entity_rank.put((-entity['doc_count'], (facet, entity['key'])))
        return entity_rank

    def show_dataset(self, dataset_id):
        entities = []
        items = self.db.search_by(facet='dataset_id', value=dataset_id)
        if items:
            title = items[0]["_source"]["raw"]["title"]
            dataset_link = "http://www.data.gv.at/katalog/dataset/%s" % dataset_id
            entities.append(self.link_decorator % (dataset_link, title))
            # get the set of formats
            formats = set([resource['format'] for resource in items[0]["_source"]["raw"]["resources"]])
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
            dataset_link = "http://www.data.gv.at/katalog/dataset/%s" % dataset_id
            formats = set([resource['format'] for resource in item["_source"]["raw"]["resources"]])
            samples.append(self.item_decorator % (dataset_link, title, " ".join(formats)))
        self.page += size
        return self.spacing.join(samples)

    def summarize_items(self):
        '''
        show summary statistics of the subset
        '''
        # reset initialize the rank for entity facet pairs by count from db
        entity_rank = self.rank_entities(entity_counts=self.aggregations)
        count, (facet, entity) = self.entity_rank.get()
        return "%sThere are %s datasets with %s as %s%s" % (self.spacing, -count, entity, facet, self.spacing)

    def show_facets(self, entity_counts=all_keywords):
        facets = []
        for facet, counts in entity_counts.items():
            facets.append(facet)
        self.start = False
        return self.spacing.join(facets)

    def show_top_entities(self):
        response = ""
        count, (facet, entity) = self.entity_rank.get()
        print facet, entity
        response += "%sThere are %s datasets with %s as %s%s" % (self.spacing, -count, entity, facet, self.spacing)
        # show examples
        results = self.db.search_by(facet=facet, value=entity)
        self.items = results['hits']['hits']
        self.aggregations = results['aggregations']
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
        return self.show_top_entities()

    def search(self, query, n_samples=5):
        self.items = self.db.search(keywords=query)
        if self.items:
            self.page = 0
            # show the top docs
            sampled_titles = self.sample_items(size=5)
            return sampled_titles
        # fall back
        else:
            return self.tell_story()

    def get_response(self, user_request):
        if user_request and len(user_request) > 2:
            return self.search(user_request)
        else:
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
    dataset_id = '71cb70af-2d7a-4b6d-811c-489f254a0353'
    print chatbot.show_dataset(dataset_id)


if __name__ == '__main__':
    test_get_CSV()
