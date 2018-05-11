# ODExploration

## Motivation

If you love #government #data but hate faceted search and csv tables? How to make your database talk? How to squeeze a table into a sequence of characters?

## Requirements

source myvenv/bin/activate

pip install -r requirements.txt

elasticsearch


## Run

To start the chatbot web UI on localhost port 8008:

python app_browse.py

python app_search.py


## Deploy

gunicorn --bind 0.0.0.0:8008 wsgi_browse:app &

gunicorn --bind 0.0.0.0:5008 wsgi_search:app &

## Stop

Ctrl+C

otherwise

kill -9 $(sudo lsof -t -i:5008)

sudo pkill python

sudo pkill gunicorn


# Interface


http://bot.communidata.at/browse
http://localhost:8008/browse


http://bot.communidata.at/search
http://localhost:8008/search

## Dataset

Datasets metadata of the Austrian Government Open Data portal (data.gv.at)

2,028 items
5 attributes: title, license, organization, categorization, tags (array 2,028+886)

2,028 items * 5 attributes (representation layers) = 10,140 information units



https://www.data.gv.at/katalog/dataset/b6385a14-b39c-4a00-a262-a8c2308759a6


## Approach

1. Index table (crawl the knowledge graph)

2. Entity ranking

        2.1 Frequency count (estimate percentage of the information space occupied by the entity)

3. Storytelling

The agent is designed to talk as long as the user is listening.

a) Storytelling approaches

        3.0. Baseline: pick entities at random.
        
        3.1. Greedy approach to storytelling is based on a pessimistic assumption that the conversation can be interupted any time. This way the agent will always communicate the most important entities first.
        
        3.2. Clustering approach to storytelling is based on an optimistic assumption that the conversation will last at least k number of turns. This way the agent can design an optimal combination of entities assuming k number of turns is available.


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

** story_size = 10

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


** story_size = 20

license
cc-by-at-30
    1852 information units per message
    102 information units per symbol
    0.18 of the information space communicated

organization
stadt-linz
stadt-wien
land-oberoesterreich
land-salzburg
stadt-innsbruck
    1535 information units per message
    31 information units per symbol
    0.30 of the information space communicated

tags
linz
haushalt
außerordentlicher
ordentlicher
finanzen
    1347 information units per message
    26 information units per symbol
    0.40 of the information space communicated

categorization
finanzen-und-rechnungswesen
umwelt
bevoelkerung
geographie-und-planung
    1181 information units per message
    20 information units per symbol
    0.47 of the information space communicated


Total: communicated 4724 information units via 232 symbols in 4 messages
    0.47 of the information space covered

* facets ranked by Gini index


(-0.75768675768675775, u'categorization')
(-0.69880119880119884, u'license')
(-0.67403120441801634, u'tags')
(-0.64241991430320344, u'organization')
(-0.019027233611292091, u'title')


categorization
finanzen-und-rechnungswesen
umwelt
bevoelkerung
geographie-und-planung
verkehr-und-technik
    794 information units per message
    7 information units per symbol
    0.08 of the information space communicated

license
cc-by-at-30
cc-by
other-pd
cc-by-sa
    1398 information units per message
    20 information units per symbol
    0.28 of the information space communicated

tags
linz
haushalt
außerordentlicher
ordentlicher
finanzen
    1255 information units per message
    19 information units per symbol
    0.37 of the information space communicated

organization
stadt-linz
stadt-wien
land-oberoesterreich
land-salzburg
stadt-innsbruck
    1246 information units per message
    18 information units per symbol
    0.49 of the information space communicated

title
Denkmalliste Steiermark
Denkmalliste Wien
Ehescheidungen
Polytechnische Schule
Sonderschulen
    999 information units per message
    13 information units per symbol
    0.49 of the information space communicated


Total: communicated 4995 information units via 365 symbols in 5 messages
    0.49 of the information space covered

### Error analysis

* search: results irrelevant to the user query

U: stadt wien
S: There are many datasets with tags: linz, haushalt, außerordentlicher, finanzen
S: For example:
Rechnungsabschluss der Stadt Wien: Ausgabenart Zeitreihe Wien
Offener Haushalt Budgetdaten Wien
Erläuterungen Subventionen Amtsbericht
Voranschlag der Landeshauptstadt Salzburg 2014
Voranschlag der Stadt Graz


## Search task

Beliebteste Vornamen in Linz:
bevoelkerung -> stadt-linz -> geschlecht


## References

* [Online JSON viewer](http://jsonviewer.stack.hu) for ES mapping
* Web UI is based on [flask-chatterbot](https://github.com/chamkank/flask-chatterbot)
* [CSS Button Generator](http://css3buttongenerator.com)
