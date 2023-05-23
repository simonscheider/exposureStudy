from rdflib import *
import owlrl
from owlrl import OWLRL_Semantics
from rdflib import Namespace
from pprint import pprint


bmo= Namespace("http://www.semanticweb.org/tabea/ontologies/2021/11/behavioural_model#")
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
    g.bind('bmo', Namespace("http://www.semanticweb.org/tabea/ontologies/2021/11/behavioural_model#"))
    g.bind('dbo', Namespace("http://dbpedia.org/ontology/"))
    g.bind('dbp', Namespace("http://dbpedia.org/resource/"))
    g.bind('dc', Namespace("http://purl.org/dc/elements/1.1/"))
    g.bind('dct', Namespace("http://purl.org/dc/terms/"))
    g.bind('dcat', Namespace("https://www.w3.org/TR/vocab-dcat-2/"))
    g.bind('prov', Namespace("http://www.w3.org/ns/prov#"))
    g.bind('rdfs', Namespace("http://www.w3.org/2000/01/rdf-schema#"))
    g.bind('owl', Namespace("http://www.w3.org/2002/07/owl#"))

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

testquery= """
SELECT DISTINCT ?causec ?causecl
WHERE {  
"""
queries = {}
queries['What are studies containing behavioral evidence for biking after 2005?']="""
SELECT DISTINCT ?cite
WHERE {  
?a a bmo:biking; bmo:StudiedChoiceOptions ?evidence.
?evidence bmo:FoundCorrelatedBy ?study.
?study bmo:HasStudyYear ?year; bmo:HasCitation ?cite.
FILTER(?year >= 2005)
}
"""
queries['What are the studies with most evidences for each behavioral choice option?']="""
SELECT  ?choice ?study ?count_evidence   
WHERE {  
SELECT DISTINCT ?study ?choice (COUNT(?evidence) as ?count_evidence)  WHERE 
{
?choice rdfs:subClassOf bmo:BehaviorChoiceOptions.
?a a ?choice; bmo:StudiedChoiceOptions ?evidence.
?evidence bmo:FoundCorrelatedBy ?study.
FILTER(?choice not in (bmo:BehaviorChoiceOptions))
} GROUP BY ?study ?choice 
ORDER BY ?choice DESC(?count_evidence)
}
"""
queries['Find studies with consistent significant evidence for walking']="""
SELECT DISTINCT ?study WHERE 
{
?a a bmo:walking; bmo:StudiedChoiceOptions ?evidence.
?evidence bmo:FoundConsistentBy ?study.
?evidence bmo:FoundSignificantBy ?study.
}
"""
queries['Find all significant behavior determinants for biking?']="""
SELECT DISTINCT ?det WHERE 
{
?a a bmo:biking; bmo:StudiedChoiceOptions ?evidence.
?evidence bmo:FoundSignificantBy ?study.
?evidence bmo:RegardsDeterminant ?det.
}
"""
queries['What are the most relevant behavioral determinants, in terms of how many behavioral choice options they significantly influence?']="""
SELECT DISTINCT ?det (COUNT(?choice) as ?count_choice) WHERE 
{
?a a ?choice; bmo:StudiedChoiceOptions ?evidence.
?evidence bmo:FoundSignificantBy ?study.
?evidence bmo:RegardsDeterminant ?det.
} GROUP BY ?det
ORDER BY DESC(COUNT(?choice))
limit 10
"""





def test(g, t = testquery):
    qres = g.query(t)
    print("now testing:")
    for row in qres:
        pprint(row)



ontology = "extendedBehaviouralModelOntology.ttl"
g = Graph()
g = load_RDF(g, ontology)
prefix(g)
# test(g)
print("Inference")
owlrl.DeductiveClosure(OWLRL_Semantics, rdfs_closure=True).expand(g)
n_triples(g)
for question in queries:
    print(question)
    test(g,queries[question])
