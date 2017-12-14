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

        3.0. Baseline: pick entities at random.
        
        3.1. Greedy approach to storytelling is based on a pessimistic assumption that the conversation can be interupted any time. This way the agent will always communicate the most important entities first.
        
        3.2. Clustering approach to storytelling is based on an optimistic assumption that the conversation will last at least k number of turns. This way the agent can design an optimal combination of entities assuming k number of turns is available.

The agent is designed to talk as long as the user is listening.

b) Optimization criteria (performance metrics of the story quality)

The agent is selecting a policy to maximize the expected reward.

Cold start + incorporating user feedback (reinforcement learning)

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
    1852 information units per message
    102 information units per symbol
    0.18 of the information space communicated

organization
stadt-linz
stadt-wien
land-oberoesterreich
    1390 information units per message
    39 information units per symbol
    0.27 of the information space communicated

tags
linz
    999 information units per message
    38 information units per symbol
    0.30 of the information space communicated

categorization
finanzen-und-rechnungswesen
    799 information units per message
    26 information units per symbol
    0.32 of the information space communicated

tags
haushalt
außerordentlicher
ordentlicher
    752 information units per message
    23 information units per symbol
    0.37 of the information space communicated

categorization
umwelt
    658 information units per message
    21 information units per symbol
    0.39 of the information space communicated


Total: communicated 3949 information units via 180 symbols in 6 messages
    0.39 of the information space covered


* clustering approach: group the top entities by attribute

license
cc-by-at-30
    1852 information units per message
    102 information units per symbol
    0.18 of the information space communicated

organization
stadt-linz
stadt-wien
land-oberoesterreich
    1390 information units per message
    39 information units per symbol
    0.27 of the information space communicated

tags
linz
haushalt
außerordentlicher
ordentlicher
    1188 information units per message
    31 information units per symbol
    0.35 of the information space communicated

categorization
finanzen-und-rechnungswesen
umwelt
    987 information units per message
    24 information units per symbol
    0.39 of the information space communicated


Total: communicated 3949 information units via 162 symbols in 4 messages
    0.39 of the information space covered


## References

* [Online JSON viewer](http://jsonviewer.stack.hu) for ES mapping
