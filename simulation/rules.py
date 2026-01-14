import random
from typing import Dict, Set
from rdflib import URIRef, Graph

from graph.eats import cleanup_dead_eats_links
from ontology.species import pop_by_species

def simulation_step_energy(
    overlay_g: Graph,
    active: Set[URIRef],
    energy: Dict[URIRef, int],
    params: dict,
    indiv_species: Dict[URIRef, str],
    species_traits: Dict[str, dict],
    species_prey: Dict[str, list],
    create_individual_fn,
    remove_individual_fn,
) -> None:
    p = params
    pop = pop_by_species(active, indiv_species)

    ate_this_step = set()

    # R1: coût de vie (sauf plantes)
    for u in list(active):
        sp = indiv_species.get(u)
        if sp and species_traits.get(sp, {}).get("is_plant", False):
            continue
        energy[u] = energy.get(u, p["E_INIT"]) - p["COST_STEP"]

    # R2: alimentation
    # 2a) Herbivores mangent plantes (densité-dépendant)
    H = 5  # demi-saturation

    plant_pools = {
        sp: pop[sp][:]
        for sp in pop
        if species_traits.get(sp, {}).get("is_plant", False)
    }
    total_plants = sum(len(v) for v in plant_pools.values())

    herb_individuals = []
    for sp, inds in pop.items():
        tr = species_traits.get(sp, {})
        if tr.get("is_herbivore", False) and not tr.get("is_carnivore", False):
            herb_individuals.extend(inds)

    random.shuffle(herb_individuals)

    for herb in herb_individuals:
        if total_plants <= 0:
            break

        p_feed = min(1.0, total_plants / (total_plants + H))
        if random.random() < p_feed:
            available_species = [sp for sp in plant_pools if len(plant_pools[sp]) > 0]
            if not available_species:
                break
            plant_sp = random.choice(available_species)
            victim = plant_pools[plant_sp].pop()

            if victim in active:
                remove_individual_fn(victim)
                ate_this_step.add(herb)
                energy[herb] = min(p["E_MAX"], energy.get(herb, p["E_INIT"]) + p["GAIN_PLANT"])
                total_plants -= 1

    # 2b) Carnivores chassent herbivores (1 tentative max / step)
    pop2 = pop_by_species(active, indiv_species)
    prey_pools = {sp: pop2[sp][:] for sp in pop2.keys()}

    for sp in list(prey_pools.keys()):
        if species_traits.get(sp, {}).get("is_plant", False):
            prey_pools.pop(sp, None)

    carn_individuals = []
    for sp, inds in pop2.items():
        tr = species_traits.get(sp, {})
        if tr.get("is_carnivore", False):
            carn_individuals.extend(inds)

    random.shuffle(carn_individuals)

    for carn in carn_individuals:
        if carn not in active:
            continue
        sp_c = indiv_species.get(carn)
        if not sp_c:
            continue
        prey_species = species_prey.get(sp_c, [])
        if not prey_species:
            continue

        candidates = [ps for ps in prey_species if ps in prey_pools and len(prey_pools[ps]) > 0]
        if not candidates:
            continue

        if random.random() < p["HUNT_PROB"]:
            prey_sp = random.choice(candidates)
            victim = prey_pools[prey_sp].pop()
            if victim in active:
                remove_individual_fn(victim)
                ate_this_step.add(carn)
                energy[carn] = min(p["E_MAX"], energy.get(carn, p["E_INIT"]) + p["GAIN_PREY"])

    # R3: mort par famine (énergie <= 0), sauf plantes
    for u in list(active):
        sp = indiv_species.get(u)
        if sp and species_traits.get(sp, {}).get("is_plant", False):
            continue
        if energy.get(u, p["E_INIT"]) <= 0:
            remove_individual_fn(u)

    cleanup_dead_eats_links(overlay_g, active)

    # R4: reproduction
    # 4a) plantes (logistique)
    pop3 = pop_by_species(active, indiv_species)
    for sp, inds in list(pop3.items()):
        tr = species_traits.get(sp, {})
        if not tr.get("is_plant", False):
            continue
        n = len(inds)
        K = p["K_PLANT"]
        if n <= 0 or n >= K:
            continue
        p_eff = p["P_REPRO_PLANT"] * max(0.0, 1.0 - (n / K))
        births = sum(1 for _ in range(n) if random.random() < p_eff)
        for _ in range(births):
            create_individual_fn(sp)

    # 4b) herbivores
    pop4 = pop_by_species(active, indiv_species)
    for sp, inds in list(pop4.items()):
        tr = species_traits.get(sp, {})
        if not (tr.get("is_herbivore", False) and not tr.get("is_carnivore", False)):
            continue
        if len(inds) < 2:
            continue
        for u in inds:
            if u not in active:
                continue
            if u not in ate_this_step:
                continue
            if energy.get(u, p["E_INIT"]) < p["E_REPRO"]:
                continue
            if random.random() < p["P_REPRO_HERB"]:
                energy[u] -= p["REPRO_COST"]
                if energy[u] > 0:
                    create_individual_fn(sp)

    # 4c) carnivores
    pop5 = pop_by_species(active, indiv_species)
    for sp, inds in list(pop5.items()):
        tr = species_traits.get(sp, {})
        if not tr.get("is_carnivore", False):
            continue
        if len(inds) < 2:
            continue
        for u in inds:
            if u not in active:
                continue
            if u not in ate_this_step:
                continue
            if energy.get(u, p["E_INIT"]) < p["E_REPRO"]:
                continue
            if random.random() < p["P_REPRO_CARN"]:
                energy[u] -= p["REPRO_COST"]
                if energy[u] > 0:
                    create_individual_fn(sp)
