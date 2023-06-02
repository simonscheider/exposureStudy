# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from rdflib import *
import owlrl
from owlrl import OWLRL_Semantics
from rdflib import Namespace
import pandas as pd
from rdflib.namespace import NamespaceManager
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
exp = Namespace("http://geographicknowledge.de/vocab/exposureBasis#")
envE = Namespace("http://geographicknowledge.de/vocab/environmentalExposure#")
envC= Namespace("http://www.geographicknowledge.de/vocab/EnvironmentalConcepts.rdf#")
ccd = Namespace("http://geographicknowledge.de/vocab/CoreConceptData.rdf#")
prov = Namespace("http://www.w3.org/ns/prov#")
owl = Namespace("http://www.w3.org/2002/07/owl#")

def prefix(g):
    g.bind('dbo', Namespace("http://dbpedia.org/ontology/"))
    g.bind('dbp', Namespace("http://dbpedia.org/resource/"))
    g.bind('dc', Namespace("http://purl.org/dc/elements/1.1/"))
    g.bind('dct', Namespace("http://purl.org/dc/terms/"))
    g.bind('dcat', Namespace("https://www.w3.org/TR/vocab-dcat-2/"))
    g.bind('exp', Namespace("http://geographicknowledge.de/vocab/exposureBasis#"))
    g.bind('envE', Namespace("http://geographicknowledge.de/vocab/environmentalExposure#"))
    g.bind('envC', Namespace("http://www.geographicknowledge.de/vocab/EnvironmentalConcepts.rdf#"))
    g.bind('ccd', Namespace("http://geographicknowledge.de/vocab/CoreConceptData.rdf#"))
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

#:Local closed world recognition
def locallyCloseWorld(g, property=exp.causedBy, all = exp.Active):
    for s in g.subjects(property, None):
        allconstraint = False
        objects = g.objects(s, property)
        for o in objects:
            #print(str(o))
            if (o, rdf.type,all) in g:
                allconstraint = True
            else:
                allconstraint = False
                break
        if allconstraint:
            #print("add all constraint for property:" +property)
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

testquery= """
SELECT DISTINCT ?causec ?causecl
WHERE {        
    ?x a exp:Exposure. 
    ?x rdfs:comment ?c.
    ?x exp:causedBy ?cause. 
    ?cause rdfs:comment ?causec.
    ?cause exp:causedBy ?ccause.
    ?ccause rdfs:comment ?ccausec.
    OPTIONAL{?ccause a ?ccausecl. FILTER(?ccausecl not in (exp:Exposure, dcat:Dataset)). FILTER(!isBlank(?ccausecl))}
    OPTIONAL{?cause a ?causecl. FILTER(?causecl not in (exp:Exposure, dcat:Dataset)). FILTER(!isBlank(?causecl))}              
}
"""
testquery2= """
SELECT DISTINCT ?c ?yc ?ycl
WHERE {      
    OPTIONAL{?x rdfs:comment ?c.}
    ?x a  ?xc.
    ?xc owl:allValuesFrom exp:Active.  
    ?x exp:causedBy ?y.
    OPTIONAL{?y rdfs:comment ?yc. } 
    OPTIONAL{?y a ?ycl. }                 
}
"""
def test(g, t = testquery2):
    qres = g.query(t)
    print("now testing:")
    for row in qres:
        print(row)



#load paper descriptions
list_of_paper_descriptions= ['Helbich_2016.ttl','Lipsett_2011.ttl','Vermeulen_2019.ttl','Rongen_2020.ttl','Grinshteyn_2018.ttl','Hillsdon_2006.ttl'] #
#list_of_paper_descriptions= ['Grinshteyn_2018.ttl'] #
basic_ontology = 'ExposureBasis.ttl'
list_of_graphs = []
for p in  list_of_paper_descriptions:
    g = Graph()
    g = load_RDF(g, p)
    load_RDF(g, basic_ontology)
    prefix(g)
    #test(g)
    print("Inference")
    owlrl.DeductiveClosure(OWLRL_Semantics, rdfs_closure=True).expand(g)
    test(g)
    locallyCloseWorld(g, property=exp.causedBy, all=exp.Active)
    #test(g)
    #g.serialize(destination=p+"test"+".ttl")
    print("Inference")
    owlrl.DeductiveClosure(OWLRL_Semantics,rdfs_closure=True).expand(g)
    list_of_graphs.append(g)
    #g.serialize(destination=p + "test" + ".ttl")
    #test(g)

#Formulate queries
queries = {}
#All tools that genereated some environmental dataset
# queries[''] = """
# SELECT DISTINCT ?cctype ?datatype ?tool
# WHERE {
#     ?x prov:wasGeneratedBy ?object .
#     ?object prov:wasAssociatedWith ?tool.
#     ?x a exp:Environment, dcat:Dataset.
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
#     ?x a exp:Environment, dcat:Dataset.
#     OPTIONAL{?x a ?y. FILTER(?y not in (exp:Environment, dcat:Dataset)).}
#     OPTIONAL{?tool rdfs:label ?l.}
# }
# """

# queries['Which tools were used in an article to measure exposures, and for which classes of exposures?'] = """
# SELECT DISTINCT ?tool ?l ?y
# WHERE {
#     ?x prov:wasGeneratedBy ?application .
#     ?application prov:wasAssociatedWith ?tool.
#     ?x a exp:Exposure, dcat:Dataset.
#     OPTIONAL{?x a ?y. FILTER(?y not in (exp:Exposure, dcat:Dataset)).}
#     OPTIONAL{?tool rdfs:label ?l.}
# }
# """

queries['What kind of exposures are modeled in this paper?'] = """
SELECT DISTINCT ?c ?y
WHERE {        
    ?x a exp:Exposure. 
    ?x rdfs:comment ?c
    OPTIONAL{?x a ?y. FILTER(?y not in (exp:Exposure, dcat:Dataset)). FILTER(!isBlank(?y))
    }              
}
"""
queries['Which activities are involved in the exposure and who is exposed?'] = """
SELECT DISTINCT ?yc ?zc
WHERE {        
    ?x a exp:Exposure. 
    ?x rdfs:comment ?xc.
    ?x exp:causedBy ?y. ?y a exp:Activity. ?y rdfs:comment ?yc.  
    OPTIONAL{?y exp:causedBy ?z. ?z a exp:Person. ?z rdfs:comment ?zc.}                      
}
"""
queries['What are subjects exposed to?'] = """
SELECT DISTINCT ?yc
WHERE    
    {
    ?x a exp:Exposure. ?x exp:causedBy ?y.  ?y rdfs:comment ?yc.
    FILTER NOT EXISTS{?x a exp:ActiveExposure. ?y a exp:EnvironmentalFactor. }     
    FILTER NOT EXISTS{?x a exp:PassiveExposure. ?y a exp:Activity. } 
}
"""
queries['What is their risk of exposure?'] = """
SELECT DISTINCT ?yc
WHERE {        
    ?x a exp:Exposure. 
    ?x rdfs:comment ?c.
    ?x exp:causes+ ?y. ?y a exp:Risk. ?y rdfs:comment ?yc.                 
}
"""
queries['Which environmental factors influence the exposure and from which datasets were they derived?'] = """
SELECT DISTINCT ?yc ?zc ?d
WHERE {        
    ?x a exp:Exposure. 
    ?x rdfs:comment ?xc.
    ?x exp:causedBy+ ?y. ?y a exp:EnvironmentalFactor. ?y rdfs:comment ?yc.
    ?y prov:wasDerivedFrom* ?z. ?z a dcat:Dataset; rdfs:comment ?zc.  
    FILTER NOT EXISTS {?z prov:wasDerivedFrom ?u}
    OPTIONAL{?z dcat:distribution ?d}                    
}
"""
queries['What are the environmental stressors?']= """
SELECT DISTINCT ?xc
WHERE {
    ?x a exp:EnvironmentalFactor; rdfs:comment ?xc. 
    ?y a exp:RiskPromotingExposure; exp:causedBy ?x .  
}
"""

pp = {}
#Run queries over articles
for idx,p in enumerate(list_of_paper_descriptions):
    paper = p.split('.')[0]
    print("paper: " + paper)
    g = list_of_graphs[idx]
    d = {}
    pp[paper]=d
    for question in queries:
        qres = g.query(queries[question])
        #print(question)
        d[question]={}
        #key = None
        #item = ''
        key = None
        for row in qres:
            for idx, r in enumerate(row):
                if isinstance(r, URIRef):
                    name = r.n3(g.namespace_manager)
                elif r is None:
                    name = 'None'
                else:
                    name = str(r)
                if idx ==0:
                    if key != name or key is None:
                        key = name
                        d[question][key]=[]
                else:
                    if name not in ('owl:Thing', 'exp:HealthRelevantExposure', 'exp:Active') and name != key:
                        (d[question][key]).append(name)



#Write all results into tables (table 2 = idx < 3 and idx >= 0; table 3 = idx < 6 and idx >= 3:)
table = []
pd.set_option('display.max_colwidth', -1)
for paper in pp.keys():
    row = pd.DataFrame()
    for idx, question in enumerate(queries):
        #if idx < 6 and idx >= 3:
        if idx < 3 and idx >= 0:
            df = pd.DataFrame({question:[], 'Context':[]})
            answers = pp[paper][question].keys()
            for a in answers:
                    context = ', '.join(pp[paper][question][a])
                    newrow= {question:a, 'Context': context}
                    df = df.append(newrow,ignore_index=True)
            #print(df)
            row = pd.concat([row,df], join = 'outer', axis = 1)

    row.insert(loc=0,column='Paper', value=paper)
    table.append(row)
table = pd.concat(table)
lat = table.to_latex(multirow=True, index =False,na_rep='',column_format=''.join(['p{1cm}']*len(table.columns))).replace('NaN', '').replace('{}', '')
#with open('table3.tex', 'w') as tf:
with open('table2.tex', 'w') as tf:
    tf.write(lat)
print(lat)
#table.append(row)
#print(table)



