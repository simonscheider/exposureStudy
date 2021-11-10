# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import rdflib
import owlrl
import os
from pprint import pprint


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

g = rdflib.Graph()

g = load_RDF(g, 'Lipsett_2011.ttl')





