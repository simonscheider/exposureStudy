# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from rdflib import *
import owlrl
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
expB = Namespace("http://geographicknowledge.de/vocab/ExposureBasis#")
envE = Namespace("http://geographicknowledge.de/vocab/environmentalExposure#")
envC= Namespace("http://www.geographicknowledge.de/vocab/EnvironmentalConcepts.rdf#")
ccd = Namespace("http://geographicknowledge.de/vocab/CoreConceptData.rdf#")
prov = Namespace("http://www.w3.org/ns/prov#")

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

g = Graph()

g = load_RDF(g, 'Lipsett_2011.ttl')



g.bind('dbo', URIRef("http://dbpedia.org/ontology/"))
g.bind('dbp', URIRef("http://dbpedia.org/resource/"))
g.bind('dc', URIRef("http://purl.org/dc/elements/1.1/"))
g.bind('dct', URIRef("http://purl.org/dc/terms/"))
g.bind('dcat', URIRef("https://www.w3.org/TR/vocab-dcat-2/"))
g.bind('expB', URIRef("http://geographicknowledge.de/vocab/ExposureBasis#"))
g.bind('envE', URIRef("http://geographicknowledge.de/vocab/environmentalExposure#"))
g.bind('envC', URIRef("http://www.geographicknowledge.de/vocab/EnvironmentalConcepts.rdf#"))
g.bind('ccd', URIRef("http://geographicknowledge.de/vocab/CoreConceptData.rdf#"))
g.bind('prov', URIRef("http://www.w3.org/ns/prov#"))

#Find all nodes that are instances of FieldQ and find their other classes
fields = g.subjects(object=ccd.FieldQ, predicate=rdf.type)
count =0
for f in fields:
    count += 1
    for o in g.objects(subject=f, predicate=rdf.type):
        pass
        #print(str(o))
#print(count)

#All tools that genereated some environmental dataset
query = """
SELECT DISTINCT ?cctype ?datatype ?tool 
WHERE {
    ?x prov:wasGeneratedBy ?object .
    ?object prov:wasAssociatedWith ?tool.
    ?x a expB:Environment, dcat:Dataset.   
    ?x a ?cctype . 
    ?x a ?datatype .
    FILTER(?cctype  in (ccd:FieldQ, ccd:ObjectQ, ccd:EventQ, ccd:NetworkQ))     
    FILTER(?datatype in (ccd:RasterA, ccd:VectorRegionA, ccd:LineA, ccd:PointA, ccd:PlainVectorRegionA, ccd:VectorTessellationA))
}"""
qres = g.query(query)
for row in qres:
    print(str(row.cctype)+ " " + str(row.datatype)+ " "+ str(row.tool))



