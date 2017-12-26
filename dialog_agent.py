'''
svakulenko
25 Dec 2017

Dialog agent class
'''
from Queue import PriorityQueue
import numpy as np

from load_ES import ESClient, INDEX_LOCAL, INDEX_SERVER, INDEX_CSV
from aggregations import all_keywords



def gini(x):
    '''
    coefficient of variation (CV) ?
    = Relative mean absolute difference (rmad) / 2
    from https://stackoverflow.com/questions/39512260/calculating-gini-coefficient-in-python-numpy
    '''
    # (Warning: This is a concise implementation, but it is O(n**2)
    # in time and memory, where n = len(x).  *Don't* pass in huge
    # samples!)

    # Mean absolute difference (standard deviation?)
    mad = np.abs(np.subtract.outer(x, x)).mean()
    # Relative mean absolute difference (average)
    mean = np.mean(x)
    # print mean
    rmad = mad/mean
    # Gini coefficient
    g = 0.5 * rmad
    return abs(g)


class DialogAgent():
    '''
    Chatbot implementing get_response method
    '''

    def __init__(self, index=INDEX_SERVER, sample=True, spacing='<br>'):
        # establish connection to the ES index
        self.db = ESClient(index)
        self.csv_db = ESClient(INDEX_CSV, host='csvengine', port=9201)
        # initialize a priority queue to store entity ranking
        self.facets_rank = self.gini_facets()
        self.entity_rank = self.rank_entities()
        self.spacing = spacing
        self.summary_facet = None
        self.keyword = None
        # self.title_decorator = "<button class='item' onclick=showDataset('%s')>%s</button>"
        self.facet_decorator = "<button class='item' onclick=showEntities('%s')>%s</button>"
        self.entity_decorator = "<button class='item' onclick=showSamples('%s','%s')>%s</button>"
        self.item_decorator = "<a class='item' href='%s'>%s</a>%s"
        self.items = []
        self.basket_limit = 5

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

    def show_facets(self):
        facets = []
        for facet, counts in all_keywords.items():
            facets.append(self.facet_decorator % (facet, facet))
        return self.spacing.join(facets)

    def gini_facets(self):
        '''
        analyse skewness of the distribution among the entites within the attribute
        compute a score for each attribute characterizing the skewness
        of the information mass distribution
        to quantify the discriminatory power of the individual factors (attributes)
        '''
        #  iterate over attributes
        facets_rank = PriorityQueue()
        for facet, counts in all_keywords.items():
            # top entities count distribution of the attribute
            distribution = [entity['doc_count'] for entity in counts['buckets']]
            # print distribution
            skewness = gini(distribution)
            facets_rank.put((-skewness, facet))
        return facets_rank

    # def show_dataset(self, dataset_id):
    #     entities = []
    #     items = self.db.search_by(facet='dataset_id', value=dataset_id)
    #     if items:
    #         title = items[0]["_source"]["raw"]["title"]
    #         dataset_link = "http://www.data.gv.at/katalog/dataset/%s" % dataset_id
    #         entities.append(self.link_decorator % (dataset_link, title))
    #         # get the set of formats
    #         formats = set([resource['format'] for resource in items[0]["_source"]["raw"]["resources"]])
    #         entities.extend(formats)

    #         if 'CSV' in formats:
    #             # get table
    #             tables = self.csv_db.search_by(facet='dataset_link', value=dataset_link)
    #             if tables:
    #                 table = tables[0]['_source']
    #                 if 'no_rows' in table.keys():
    #                     facet = 'no_rows'
    #                     entities.append('%s: %s' % (facet, table[facet]))
            
    #         return self.spacing + self.spacing.join(entities)

    def sample_items(self, size):
        '''
        show a sample of items for an entity
        '''
        samples = []
        if self.items:
            for item in self.items[self.page:self.page+size]:
                # get title
                title = item["_source"]["raw"]["title"]
                dataset_id = item["_source"]["raw"]["id"]
                dataset_link = "http://www.data.gv.at/katalog/dataset/%s" % dataset_id
                formats = set([resource['format'] for resource in item["_source"]["raw"]["resources"]])
                samples.append(self.item_decorator % (dataset_link, title, " ".join(formats)))
            self.page += size
            return self.spacing.join(samples)
        else:
            return self.tell_story()

    def summarize_items(self):
        '''
        show summary statistics of the subset
        '''
        # get facet-entity subset of the dataset
        if self.keyword:
            counts = self.db.describe_subset(keywords=self.keyword)
            if self.summary_facet != self.keyword:
                self.summary_rank = self.rank_entities(counts)
                self.summary_facet = self.keyword
            count, (facet, entity) = self.summary_rank.get()
            entity = self.entity_decorator % (facet, entity, entity)
            facet = self.facet_decorator % (facet, facet)
            return "There are %s datasets with %s as %s%s" % (-count, entity, facet, self.spacing)
        elif self.facet:
            counts = self.db.aggregate_entity(facet=self.facet, value=self.entity)
            if self.summary_facet != self.facet:
                self.summary_rank = self.rank_entities(counts)
                self.summary_facet = self.facet
            count, (facet, entity) = self.summary_rank.get()
            entity = self.entity_decorator % (facet, entity, entity)
            return "%sAmong %s there are %s datasets with %s as %s%s" % (self.spacing, self.entity, -count, entity, facet, self.spacing)

    def search_by(self, facet, entity, size=5):
        # show examples
        items = self.db.search_by(facet=facet, value=entity)
        # show only new items
        # self.items = list(set([item["_source"]["raw"]["title"] for item in items]) - self.shown)
        if items:
            self.items = items
            self.facet = facet
            self.entity = entity

            self.page = 0
            sampled_titles = self.sample_items(size=size)
            return "%sAmong %s there are%s" % (self.spacing, entity, self.spacing) + sampled_titles

    def show_top_entities(self):
        response = ""
        count, (facet, entity) = self.entity_rank.get()
        response += "%sThere are %s datasets with %s as %s%s" % (self.spacing, -count, self.entity, self.facet, self.spacing)
        result = self.search_by(facet, entity)
        if result:
            return response + result
        else:
            # try another entity
            return self.show_top_entities()

    def show_top_facets(self):
        count, facet = self.facets_rank.get()
        entities = []
        for entity in all_keywords[facet]['buckets'][:self.basket_limit]:
            entities.append(self.entity_decorator % (facet, entity['key'], entity['key']))
        return "%s:%s%s" % (facet, self.spacing, self.spacing.join(entities))

    def tell_story(self):
        return self.show_top_facets()

    def search(self, query, n_samples=5):
        self.items = self.db.search(keywords=query)
        if self.items:
            self.keyword = query
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
