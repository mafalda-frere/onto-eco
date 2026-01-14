import random
from rdflib import URIRef, RDF
from rdflib import Graph
from typing import Dict, Set

from ontology.loader import AWO4
from ontology.species import local_name
from graph.eats import add_edges_for_new_individual

def create_individual(
    overlay_g: Graph,
    active: Set[URIRef],
    energy: Dict[URIRef, int],
    params: dict,
    indiv_species: Dict[URIRef, str],
    known_species: Set[str],
    species_prey: dict,
    species_str: str,
) -> URIRef:
    uri = AWO4[f"{local_name(species_str).lower()}{random.randint(1000,9999)}"]
    overlay_g.add((uri, RDF.type, URIRef(species_str)))
    active.add(uri)

    indiv_species[uri] = species_str
    known_species.add(species_str)
    energy[uri] = params["E_INIT"]

    # edges locales si rules déjà construites
    if species_prey:
        add_edges_for_new_individual(overlay_g, active, indiv_species, species_prey, uri)

    return uri

def remove_individual(
    overlay_g: Graph,
    active: Set[URIRef],
    energy: Dict[URIRef, int],
    indiv_species: Dict[URIRef, str],
    u: URIRef,
) -> None:
    active.discard(u)
    indiv_species.pop(u, None)
    energy.pop(u, None)

    # enlever triples liés dans overlay
    for t in list(overlay_g.triples((u, None, None))) + list(overlay_g.triples((None, None, u))):
        overlay_g.remove(t)
