'''
svakulenko
25 Dec 2017

Dialog agent class
'''
from collections import Counter
from Queue import PriorityQueue
import numpy as np

from load_ES import ESClient, INDEX_LOCAL, INDEX_SERVER, INDEX_CSV
from aggregations import all_keywords


INDEX = INDEX_SERVER


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

    def __init__(self, index=INDEX, sample=True, spacing='<br>'):
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
        # self.entity_decorator = "<button class='item' onclick=showSamples('%s','%s')>%s</button>"
        self.entity_decorator = "<button class='item' onclick=pivotEntity({%s})>%s</button>"
        # self.entity_decorator = "<button class='item' onclick=pivotEntity(%s)>%s</button>"
        self.item_decorator = "<a class='item' href='%s'>%s</a>%s"

        # container for current entities
        self.entities = []

        # container for current items
        self.items = []

        # cursor for interating over the list of entities and items
        self.page = 0
        # maximum number of nodes revealed in one reply
        self.basket_limit = 5
        # keep focus on the current listing
        self.focus = None
        # store currently pivoted facets
        self.facets_values = []

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

    def sample_nodes(self, size):
        '''
        show a sample of items or entities
        '''
        if self.focus == 'pivot':
            return self.show_entities()
        elif self.focus == 'titles' and self.items:
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
        elif self.page < len(self.entities):
            return self.show_facet_entities()
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
            self.facets_values.append((self.facet, self.entity))
            entities = " ".join([entity for (facet, entity) in self.facets_values])
            counts = self.db.summarize_subset(facets_values=self.facets_values)
            if self.summary_facet != self.facet:
                self.summary_rank = self.rank_entities(counts)
                self.summary_facet = self.facet
            count, (facet, entity) = self.summary_rank.get()
            entity = self.entity_decorator % (facet, entity, entity)
            return "%sAmong %s there are %s datasets with %s as %s%s" % (self.spacing, entities, -count, entity, facet, self.spacing)

    def subset(self, facet, entity):
        response = "%sFor %s there are%s" % (self.spacing, entity, self.spacing)
        response += self.search_by(facet, entity)
        return response

    def show_entities(self):
        # show top entities of the pivoted subset
        entities = []
        # start listing entities
        for i in range(self.basket_limit):
            count, (facet, entity) = self.summary_rank.get()
            print facet, entity
            # skip non-discriminative attributes
            if -count > self.n_items - 2:
                continue
            if -count < 2:
                break
            facet_strings = ["'%s':'%s'" % (facet, entity)]
            # attach all previous pivoted entities
            for _facet, _entity in self.facets_values.items():
                facet_strings.append("'%s':'%s'" % (_facet, _entity))
            entity_button = self.entity_decorator % (','.join(facet_strings), entity)
            entities.append("%d datasets with %s as %s" % (-count, entity_button, facet))
        return self.spacing.join(entities)

    def create_title_link(self, item):
        # get title
        title = item["_source"]["raw"]["title"]
        dataset_id = item["_source"]["raw"]["id"]
        dataset_link = "http://www.data.gv.at/katalog/dataset/%s" % dataset_id
        formats = Counter()
        for resource in item["_source"]["raw"]["resources"]:
            formats[resource['format']] += 1
        response = self.item_decorator % (dataset_link, title, str(formats))
        # if 'CSV' in formats.keys():
        #     # get table
        #     tables = self.csv_db.search_by(facet='dataset_link', value=dataset_link)
        #     if tables:
        #         table = tables[0]['_source']
        #         if 'no_rows' in table.keys():
        #             facet = 'no_rows'
        #             response += ' %s: %s' % (facet, table[facet])
        return response

    def show_sample(self, size):
        self.page = 0
        samples = []
        for item in self.items[self.page:self.page+size]:
            samples.append(self.create_title_link(item))
        self.page += size
        entities = ' '.join(self.facets_values.values())
        self.focus = "titles"
        return "%s%d datasets for %s, e.g.:%s" % (self.spacing, self.n_items, entities, self.spacing) + self.spacing.join(samples)

    def pivot(self, facets_values):
        '''
        traverse the subtree
        '''
        self.page = 0
        result = self.db.summarize_subset(facets_values=facets_values)
        items = result['hits']['hits']
        if items:
            self.items = items
            self.facets_values = facets_values
            self.n_items = len(items)
            if self.n_items < self.basket_limit:
                return self.show_sample(size=self.basket_limit)
            else:
                counts = result['aggregations']
                # order entities
                self.summary_rank = self.rank_entities(counts)
                entities = ' '.join(self.facets_values.values())
                summary = self.show_entities()
                if summary:
                    self.focus = "pivot"
                    return "%sAmong %s there are %d datasets%s"  % (self.spacing, entities, self.n_items, self.spacing) + summary
                else:
                    return self.show_sample(size=self.basket_limit)
        else:
            # fall back to story telling
            return self.tell_story()

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
            sampled_titles = self.sample_nodes(size=size)
            return sampled_titles

    def show_top_entities(self):
        response = ""
        count, (facet, entity) = self.entity_rank.get()
        response += "%sThere are %s datasets with %s as %s%s" % (self.spacing, -count, entity, facet, self.spacing)
        # show sample dataset titles for the facet-entity combination
        result = self.search_by(facet, entity)
        if result:
            response += "%sFor example%s" % (self.spacing, self.spacing) 
            return response + result
        else:
            # try another entity
            return self.show_top_entities()

    def show_top_facet(self):
        count, facet = self.facets_rank.get()
        self.entities = all_keywords[facet]['buckets']
        self.items = []
        self.page = 0
        self.facet = facet
        return self.show_facet_entities()

    def show_facet_entities(self):
        '''
        show top entities of the facet
        '''
        entities = []
        # start listing entities
        response = ""
        if self.page == 0:
            response +=  "%sDatasets have %d different %s, e.g.:%s" % (self.spacing, len(self.entities), self.facet, self.spacing)
        for entity in self.entities[self.page:self.page+self.basket_limit]:
            # facets_value = "[['%s', '%s']]" % (self.facet, entity['key'])
            # facets_value = "['%s', '%s']" % (self.facet, entity['key'])
            # entities.append(self.entity_decorator % (facets_value, entity['key']))
            facet_value = "'%s':'%s'" % (self.facet, entity['key'])
            entities.append(self.entity_decorator %  (facet_value, entity['key']))
        self.page += self.basket_limit
        response += self.spacing.join(entities)
        print response
        return response

    def tell_story(self):
        # show facets and entities starting from the most important/frequent ones
        if not self.facets_rank.empty():
            # iterate over the facets rank
            return self.show_top_facet()
        else:
            # iterate over the entities rank
            return self.show_top_entities()

    def search(self, query, n_samples=5):
        self.items = self.db.search(keywords=query)
        if self.items:
            self.keyword = query
            self.page = 0
            # show the top docs
            sampled_titles = self.sample_nodes(size=5)
            return sampled_titles
        # fall back
        else:
            return self.tell_story()

    def get_response(self, user_request):
        '''
        main entry for the dialog agent response
        '''
        if user_request and len(user_request) > 2:
            # perform search using the user input as the query string
            return self.search(user_request)
        else:
            # show facets and entities of the dataset
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
            print chatbot.sample_nodes(size=10)
            print '\n'


def test_get_CSV(index=INDEX_SERVER):
    chatbot = DialogAgent(index, spacing='\n')
    dataset_id = '71cb70af-2d7a-4b6d-811c-489f254a0353'
    print chatbot.show_dataset(dataset_id)


if __name__ == '__main__':
    test_get_CSV()
