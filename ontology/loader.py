from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, OWL

AWO1 = Namespace("http://www.meteck.org/teaching/OEbook/ontologies/AfricanWildlifeOntology1.owl#")
AWO4 = Namespace("http://www.meteck.org/teaching/OEbook/ontologies/AfricanWildlifeOntology4.owl#")

ANIMAL = AWO1.Animal
PLANT = AWO1.Plant
EATS = AWO1.eats
BIOLOGICAL_SPECIES = AWO4.BiologicalSpecies

def load_base_graph(path: str) -> Graph:
    g = Graph()
    g.parse(path, format="xml")
    return g

def new_overlay_graph() -> Graph:
    g = Graph()
    g.bind("awo1", AWO1)
    g.bind("awo4", AWO4)
    return g
