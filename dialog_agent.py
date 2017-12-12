'''
svakulenko
12 Dec 2017

Create sample utterances from data
'''
from aggregations import counts, top_keywords


def list_facets_counts():
    stats = []
    for facet, count in counts.items():
        stats.append("%s %s" % (count['value'] , facet))

    stats_string = "There are " + ", ".join(stats)
    print stats_string


def facets_top_entities(k=2):
    stats = []
    for facet, count in top_keywords.items():
        top_entities = []
        for rank in range(k):
            top_entities.append(count['buckets'][rank]['key'])

        stats.append("%s are the most popular among %s" % (" and ".join(top_entities), facet))

    stats_string = "\n".join(stats)
    print stats_string


def main():
    facets_top_entities()


if __name__ == '__main__':
    main()
