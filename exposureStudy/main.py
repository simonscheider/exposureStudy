# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from rdflib import *
import owlrl
from owlrl import OWLRL_Semantics
import os
from pprint import pprint
from SPARQLWrapper import SPARQLWrapper, JSON


dbo = Namespace("http://dbpedia.org/ontology/")
dbp = Namespace("http://dbpedia.org/resource/")
dc = Namespace("http://purl.org/dc/elements/1.1/")
dct = Namespace("http://purl.org/dc/terms/")
dcat= Namespace("https://www.w3.org/TR/vocab-dcat-2/")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
expB = Namespace("http://geographicknowledge.de/vocab/exposureBasis#")
envE = Namespace("http://geographicknowledge.de/vocab/environmentalExposure#")
envC= Namespace("http://www.geographicknowledge.de/vocab/EnvironmentalConcepts.rdf#")
ccd = Namespace("http://geographicknowledge.de/vocab/CoreConceptData.rdf#")
prov = Namespace("http://www.w3.org/ns/prov#")
owl = Namespace("http://www.w3.org/2002/07/owl#")

def prefix(g):
    g.bind('dbo', URIRef("http://dbpedia.org/ontology/"))
    g.bind('dbp', URIRef("http://dbpedia.org/resource/"))
    g.bind('dc', URIRef("http://purl.org/dc/elements/1.1/"))
    g.bind('dct', URIRef("http://purl.org/dc/terms/"))
    g.bind('dcat', URIRef("https://www.w3.org/TR/vocab-dcat-2/"))
    g.bind('expB', URIRef("http://geographicknowledge.de/vocab/exposureBasis#"))
    g.bind('envE', URIRef("http://geographicknowledge.de/vocab/environmentalExposure#"))
    g.bind('envC', URIRef("http://www.geographicknowledge.de/vocab/EnvironmentalConcepts.rdf#"))
    g.bind('ccd', URIRef("http://geographicknowledge.de/vocab/CoreConceptData.rdf#"))
    g.bind('prov', URIRef("http://www.w3.org/ns/prov#"))
    g.bind('rdfs', URIRef("http://www.w3.org/2000/01/rdf-schema#"))
    g.bind('owl', URIRef("http://www.w3.org/2002/07/owl#"))

def n_triples( g, n=None ):
    """ Prints the number of triples in graph g """
    if n is None:
        print( '  Triples: '+str(len(g)) )
    else:
        print( '  Triples: +'+str(len(g)-n) )
    return len(g)

def load_RDF( g, fn ):
    print("load_RDF: "+fn)
    g.parse( fn , format='turtle')
    n_triples(g)
    return g

#:Local closed world recognition
def locallyCloseWorld(g, property=expB.causedBy, all = expB.Activity):
    for s in g.subjects(property, None):
        allconstraint = False
        objects = g.objects(s, property)
        for o in objects:
            #print(str(o))
            if (o, rdf.type,all) in g:
                allconstraint = True
            else:
                allconstraint = False
        if allconstraint:
            print("add all constraint for property:" +property)
            # """
            # [ rdf:type owl:Restriction ;
            #         owl:onProperty :causedBy ;
            #         owl:allValuesFrom :Activity
            # ]
            # """
            constr = BNode()
            g.add((s, rdf.type,constr))
            g.add((constr, rdf.type,owl.Restriction))
            g.add((constr,owl.onProperty, property))
            g.add((constr,owl.allValuesFrom, all))



#load paper descriptions
list_of_paper_descriptions= ['Helbich_2016.ttl']
basic_ontology = 'ExposureBasis.ttl'
list_of_graphs = []
for p in  list_of_paper_descriptions:
    g = Graph()
    g = load_RDF(g, p)
    load_RDF(g, basic_ontology)
    prefix(g)
    print("Inference")
    owlrl.DeductiveClosure(OWLRL_Semantics, rdfs_closure=True).expand(g)
    locallyCloseWorld(g, property=expB.causedBy, all=expB.Activity)
    print("Inference")
    owlrl.DeductiveClosure(OWLRL_Semantics,rdfs_closure=True).expand(g)
    list_of_graphs.append(g)

#load ontology
#load_RDF(g, 'ExposureBasis.ttl')

#Add local closed world assumption for causal inference:




#Find all nodes that are instances of FieldQ and find their other classes
# fields = g.subjects(object=ccd.FieldQ, predicate=rdf.type)
# count =0
# for f in fields:
#     count += 1
#     for o in g.objects(subject=f, predicate=rdf.type):
#         pass
#         #print(str(o))
#print(count)

#All tools that genereated some environmental dataset
queries = {}
# queries[''] = """
# SELECT DISTINCT ?cctype ?datatype ?tool
# WHERE {
#     ?x prov:wasGeneratedBy ?object .
#     ?object prov:wasAssociatedWith ?tool.
#     ?x a expB:Environment, dcat:Dataset.
#     ?x a ?cctype .
#     ?x a ?datatype .
#     FILTER(?cctype  in (ccd:FieldQ, ccd:ObjectQ, ccd:EventQ, ccd:NetworkQ))
#     FILTER(?datatype in (ccd:RasterA, ccd:VectorRegionA, ccd:LineA, ccd:PointA, ccd:PlainVectorRegionA, ccd:VectorTessellationA))
# }"""
# queries['Which tools were used in an article to measure environments, and for which classes of environments?'] = """
# SELECT DISTINCT ?tool ?l ?y
# WHERE {
#     ?x prov:wasGeneratedBy ?application .
#     ?application prov:wasAssociatedWith ?tool.
#     ?x a expB:Environment, dcat:Dataset.
#     OPTIONAL{?x a ?y. FILTER(?y not in (expB:Environment, dcat:Dataset)).}
#     OPTIONAL{?tool rdfs:label ?l.}
# }
# """

# queries['Which tools were used in an article to measure exposures, and for which classes of exposures?'] = """
# SELECT DISTINCT ?tool ?l ?y
# WHERE {
#     ?x prov:wasGeneratedBy ?application .
#     ?application prov:wasAssociatedWith ?tool.
#     ?x a expB:Exposure, dcat:Dataset.
#     OPTIONAL{?x a ?y. FILTER(?y not in (expB:Exposure, dcat:Dataset)).}
#     OPTIONAL{?tool rdfs:label ?l.}
# }
# """

queries['What kind of exposures are modeled in this paper?'] = """
SELECT DISTINCT ?x ?c ?y
WHERE {        
    ?x a expB:Exposure. 
    ?x rdfs:comment ?c
    OPTIONAL{?x a ?y. FILTER(?y not in (expB:Exposure, dcat:Dataset)). FILTER(!isBlank(?y))
    }              
}
"""
queries['Which activities cause exposure and who is exposed?'] = """
SELECT DISTINCT ?xc ?yc ?zc
WHERE {        
    ?x a expB:Exposure. 
    ?x rdfs:comment ?xc.
    ?x expB:causedBy ?y. ?y a expB:Activity. ?y rdfs:comment ?yc.
    ?y expB:causedBy ?z. ?z a expB:Person. ?z rdfs:comment ?zc.                   
}
"""
for idx,p in enumerate(list_of_paper_descriptions):
    print("paper: " + p)
    g = list_of_graphs[idx]
    for question in queries:
        qres = g.query(queries[question])
        print(question)
        for row in qres:
            print(str(row))



