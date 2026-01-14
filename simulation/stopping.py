from ontology.species import pop_by_species

def update_history_and_check_stop(active, indiv_species, history: dict, known_species: set, t: int, params: dict):
    pop = pop_by_species(active, indiv_species)

    # ajouter toutes espèces vues
    for sp in list(known_species):
        history.setdefault(sp, [])

    # append counts (0 si absente)
    for sp in list(history.keys()):
        history[sp].append(len(pop.get(sp, [])))

    if len(active) == 0:
        return "EXTINCTION"

    W = params["stable_window"]
    R = params["stable_range"]
    if t >= W:
        stable = True
        for hist in history.values():
            if len(hist) < W:
                stable = False
                break
            recent = hist[-W:]
            if max(recent) - min(recent) > R:
                stable = False
                break
        if stable:
            return "STABLE"

    if t >= params["max_steps"]:
        return "TIMEOUT"

    return None
