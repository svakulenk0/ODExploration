# ODExploration

## Dataset

Datasets metadata of the Austrian Government Open Data portal (data.gv.at)

2,028 items
5 attributes: title, license, organization, categorization, tags (array)
3,064 entities

2,028 items * 5 attributes (representation layers) = 10,140 information items


## Approach

1. Index dataset (Lucene/ES)
2. Rank entities using counts


## Entity ranking

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


## References

* [Online JSON viewer](http://jsonviewer.stack.hu) for ES mapping
