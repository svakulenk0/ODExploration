# ODExploration

## Dataset

Datasets metadata of the Austrian Government Open Data portal (data.gv.at)

2,028 items
5 attributes: title, license, organization, categorization, tags (array)
3,064 entities

2,028 items * 5 attributes (representation layers) = 10,140 information units


## Approach

1. Index table (or crawl the knowledge graph)

2. Entity ranking

        2.1 Count (estimate percentage of the information space occupied by the entity)

3. Storytelling

a) Storytelling approaches
        
        3.1. Greedy approach to storytelling is based on a pessimistic assumption that the conversation can be interupted any time. This way the agent will always communicate the most important entities first.
        
        3.2. Clustering approach to storytelling is based on an optimistic assumption that the conversation will last at least k number of turns. This way the agent can design an optimal combination of entities assuming k number of turns is available.

The agent is designed to talk as long as the user is listening.

b) Optimization criteria (performance metrics of the story quality)

The agent is selecting a policy to maximize the expected reward.

Cold start + incorporating user feedback (reinforcement learning).

Information space coverage is the sum of the weights of all the entities communicated up to the ith point of time. The weights are derived from the entity ranking, e.g. counts. This measure can be converted into a proportion (%) with respect to the whole information space (normalised by the size of the input table).

We also design an information theory-inspired measure of information units per symbol to measure communication efficiency.



## Results

* Top 10 entities by count

(-1852, (u'license', u'cc-by-at-30'))
(-351, (u'organization', u'stadt-linz'))
(-335, (u'organization', u'stadt-wien'))
(-242, (u'organization', u'land-oberoesterreich'))
(-218, (u'tags', u'linz'))
(-198, (u'categorization', u'finanzen-und-rechnungswesen'))
(-191, (u'tags', u'haushalt'))
(-188, (u'tags', u'au\xdferordentlicher'))
(-188, (u'tags', u'ordentlicher'))
(-186, (u'categorization', u'{umwelt}'))


Experiment_1: max story size = 10 entities


* greedy approach: max counts first priority queue

license
cc-by-at-30
        102 information units per symbol
organization
stadt-linz
        55 information units per symbol
stadt-wien
        50 information units per symbol
land-oberoesterreich
        39 information units per symbol
tags
linz
        38 information units per symbol
categorization
finanzen-und-rechnungswesen
        26 information units per symbol
tags
haushalt
        25 information units per symbol
außerordentlicher
        24 information units per symbol
ordentlicher
        23 information units per symbol
categorization
umwelt
        21 information units per symbol

Total: communicated 3949 information units via 180 symbols


* clustering approach: group all entities by attribute





## References

* [Online JSON viewer](http://jsonviewer.stack.hu) for ES mapping
