import random
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Any

from rdflib import Graph, URIRef, RDF
from rdflib.namespace import RDFS, OWL

from .loader import AWO1, AWO4, PLANT, EATS, BIOLOGICAL_SPECIES

def local_name(uri) -> str:
    s = str(uri)
    return s.split("#")[-1] if "#" in s else s.rsplit("/", 1)[-1]

def is_subclass_of(g: Graph, cls: URIRef, parent: URIRef) -> bool:
    visited = set()
    stack = [cls]
    while stack:
        c = stack.pop()
        if c == parent:
            return True
        for sup in g.objects(c, RDFS.subClassOf):
            if sup not in visited:
                visited.add(sup)
                stack.append(sup)
    return False

def list_species(base_g: Graph) -> List[str]:
    out = []
    for cls in base_g.subjects(RDF.type, OWL.Class):
        s = str(cls)
        if s.startswith(str(OWL)) or s.startswith(str(RDFS)):
            continue
        if is_subclass_of(base_g, cls, BIOLOGICAL_SPECIES) or is_subclass_of(base_g, cls, PLANT):
            out.append(s)
    return sorted(out)

class EatsRulesCache:
    def __init__(self):
        self._class_eats_cache = None

    def class_level_eats_relations(self, base_g: Graph) -> List[Tuple[URIRef, URIRef]]:
        if self._class_eats_cache is not None:
            return self._class_eats_cache

        q = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX awo: <http://www.meteck.org/teaching/OEbook/ontologies/AfricanWildlifeOntology1.owl#>

        SELECT ?pred ?prey WHERE {
          ?pred rdfs:subClassOf [
            a owl:Restriction ;
            owl:onProperty awo:eats ;
            owl:someValuesFrom ?prey
          ] .
        }
        """
        self._class_eats_cache = [(row.pred, row.prey) for row in base_g.query(q)]
        return self._class_eats_cache

def _depth(g: Graph, cls: URIRef) -> int:
    d = 0
    stack = [cls]
    seen = set()
    while stack:
        c = stack.pop()
        for sup in g.objects(c, RDFS.subClassOf):
            if sup not in seen:
                seen.add(sup)
                d += 1
                stack.append(sup)
    return d

def most_specific_species_class(g: Graph, u: URIRef) -> URIRef | None:
    candidates = []
    for t in g.objects(u, RDF.type):
        if is_subclass_of(g, t, BIOLOGICAL_SPECIES) or is_subclass_of(g, t, PLANT):
            candidates.append(t)
    if not candidates:
        return None
    return max(candidates, key=lambda c: _depth(g, c))

def pop_by_species(active: Set[URIRef], indiv_species: Dict[URIRef, str]):
    pop = defaultdict(list)
    for u in list(active):
        sp = indiv_species.get(u)
        if sp:
            pop[sp].append(u)
    return pop

def rebuild_species_mapping_and_rules(
    reasoned_g: Graph,
    active: Set[URIRef],
    eats_cache: EatsRulesCache,
    base_g: Graph,
    indiv_species: Dict[URIRef, str],
    species_traits: Dict[str, dict],
    species_prey: Dict[str, List[str]],
    known_species: Set[str],
) -> None:
    """
    Rebuild:
    - INDIV_SPECIES
    - SPECIES_TRAITS
    - SPECIES_PREY
    - KNOWN_SPECIES
    """
    indiv_species.clear()
    species_traits.clear()
    species_prey.clear()
    known_species.clear()

    # individu -> espèce (classe la plus spécifique)
    for u in list(active):
        sp = most_specific_species_class(reasoned_g, u)
        if sp is None:
            continue
        indiv_species[u] = str(sp)
        known_species.add(str(sp))

    # traits par espèce
    for sp_str in set(indiv_species.values()):
        sp = URIRef(sp_str)
        species_traits[sp_str] = {
            "is_plant": is_subclass_of(reasoned_g, sp, PLANT),
            "is_carnivore": is_subclass_of(reasoned_g, sp, AWO1.Carnivore),
            "is_herbivore": is_subclass_of(reasoned_g, sp, AWO1.Herbivore),
        }

    # règles eats au niveau espèces
    rules = eats_cache.class_level_eats_relations(base_g)
    species_list = list(set(indiv_species.values()))

    subclass_cache: Dict[tuple, bool] = {}

    def is_sub(sp_str: str, cls: URIRef) -> bool:
        key = (sp_str, str(cls))
        if key in subclass_cache:
            return subclass_cache[key]
        res = is_subclass_of(reasoned_g, URIRef(sp_str), cls)
        subclass_cache[key] = res
        return res

    for pred_sp in species_list:
        prey_list = []
        for pred_cls, prey_cls in rules:
            if not is_sub(pred_sp, pred_cls):
                continue
            for prey_sp in species_list:
                if prey_sp == pred_sp:
                    continue
                if is_sub(prey_sp, prey_cls):
                    prey_list.append(prey_sp)
        species_prey[pred_sp] = sorted(set(prey_list))
