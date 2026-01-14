from rdflib import Graph, URIRef
from typing import Dict, List, Set

from ontology.loader import EATS

def cleanup_dead_eats_links(overlay_g: Graph, active: Set[URIRef]) -> None:
    for s, p, o in list(overlay_g.triples((None, EATS, None))):
        if s not in active or o not in active:
            overlay_g.remove((s, p, o))

def add_edges_for_new_individual(
    overlay_g: Graph,
    active: Set[URIRef],
    indiv_species: Dict[URIRef, str],
    species_prey: Dict[str, List[str]],
    u: URIRef
) -> None:
    sp_u = indiv_species.get(u)
    if not sp_u:
        return

    # u comme prédateur
    prey_species = species_prey.get(sp_u, [])
    for v in list(active):
        if v == u:
            continue
        sp_v = indiv_species.get(v)
        if sp_v and sp_v in prey_species:
            overlay_g.add((u, EATS, v))

    # u comme proie
    for v in list(active):
        if v == u:
            continue
        sp_v = indiv_species.get(v)
        if not sp_v:
            continue
        prey_species_v = species_prey.get(sp_v, [])
        if sp_u in prey_species_v:
            overlay_g.add((v, EATS, u))

def auto_generate_eats_links_full(
    overlay_g: Graph,
    active: Set[URIRef],
    indiv_species: Dict[URIRef, str],
    species_prey: Dict[str, List[str]]
) -> None:
    cleanup_dead_eats_links(overlay_g, active)
    for u in list(active):
        sp_u = indiv_species.get(u)
        if not sp_u:
            continue
        prey_species = set(species_prey.get(sp_u, []))
        for v in list(active):
            if u == v:
                continue
            sp_v = indiv_species.get(v)
            if sp_v and sp_v in prey_species:
                overlay_g.add((u, EATS, v))
