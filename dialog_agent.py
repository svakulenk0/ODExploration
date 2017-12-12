'''
svakulenko
12 Dec 2017

Create sample utterances from data
'''
from load_ES import ESClient
from aggregations import counts, top_keywords


def list_facets_counts():
    '''
    counts of entities for each attribute
    '''
    stats = []
    for facet, count in counts.items():
        stats.append("%s %s" % (count['value'] , facet))

    stats_string = "There are " + ", ".join(stats)
    print stats_string


def facets_top_entities(k=2):
    '''
    top entities for each attribute
    '''
    stats = []
    for facet, count in top_keywords.items():
        top_entities = []
        for rank in range(k):
            top_entities.append(count['buckets'][rank]['key'])

        stats.append("%s are the most popular among %s" % (" and ".join(top_entities), facet))

    stats_string = "\n".join(stats)
    print stats_string


def sample_items():
    '''
    show a sample of items for an entity
    '''
    db = ESClient()
    results = db.search_by(field="raw.license_id.keyword", value="cc-by-at-30", limit=5)
    for item in results:
        print item["raw"]["title"]


def main():
    sample_items()


if __name__ == '__main__':
    main()
