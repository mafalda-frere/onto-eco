from flask import Blueprint, jsonify, request
from rdflib import URIRef, RDF

from ontology.species import is_subclass_of, local_name
from ontology.loader import BIOLOGICAL_SPECIES, PLANT, AWO4
from ontology.species import rebuild_species_mapping_and_rules, pop_by_species
from graph.eats import auto_generate_eats_links_full, cleanup_dead_eats_links
from simulation.rules import simulation_step_energy
from simulation.stopping import update_history_and_check_stop

def build_simulation_bp(ctx):
    bp = Blueprint("simulation", __name__)

    @bp.post("/add_individual")
    def api_add_individual():
        if ctx["state"].running:
            return jsonify({"ok": False, "error": "Simulation en cours"}), 400

        data = request.get_json(force=True)
        species_uri = URIRef(data["species"])

        if not (is_subclass_of(ctx["base_g"], species_uri, BIOLOGICAL_SPECIES) or is_subclass_of(ctx["base_g"], species_uri, PLANT)):
            return jsonify({"ok": False, "error": "Classe non supportée"}), 400

        uri = AWO4[f"{local_name(species_uri).lower()}{ctx['rng']()}"]
        ctx["overlay_g"].add((uri, RDF.type, species_uri))
        ctx["state"].active.add(uri)
        ctx["state"].energy[uri] = ctx["state"].params["E_INIT"]

        ctx["reasoner"].mark_dirty()
        return jsonify({"ok": True, "id": str(uri)})

    @bp.post("/remove_individual")
    def api_remove_individual():
        if ctx["state"].running:
            return jsonify({"ok": False, "error": "Simulation en cours"}), 400

        uri = URIRef(request.get_json(force=True)["id"])

        # remove
        ctx["state"].active.discard(uri)
        ctx["indiv_species"].pop(uri, None)
        ctx["state"].energy.pop(uri, None)
        for t in list(ctx["overlay_g"].triples((uri, None, None))) + list(ctx["overlay_g"].triples((None, None, uri))):
            ctx["overlay_g"].remove(t)

        cleanup_dead_eats_links(ctx["overlay_g"], ctx["state"].active)
        ctx["reasoner"].mark_dirty()
        return jsonify({"ok": True})

    @bp.post("/auto_eats")
    def api_auto_eats():
        if ctx["state"].running:
            return jsonify({"ok": False, "error": "Simulation en cours"}), 400

        # reason + rebuild mapping/rules + edges
        g = ctx["reasoner"].reasoned_graph(ctx["base_g"], ctx["overlay_g"], freeze_ok=False, frozen_reasoner=False)
        rebuild_species_mapping_and_rules(
            reasoned_g=g,
            active=ctx["state"].active,
            eats_cache=ctx["eats_cache"],
            base_g=ctx["base_g"],
            indiv_species=ctx["indiv_species"],
            species_traits=ctx["species_traits"],
            species_prey=ctx["species_prey"],
            known_species=ctx["state"].known_species,
        )
        auto_generate_eats_links_full(ctx["overlay_g"], ctx["state"].active, ctx["indiv_species"], ctx["species_prey"])
        ctx["reasoner"].mark_dirty()
        return jsonify({"ok": True})

    @bp.post("/start")
    def api_start():
        # 1) calc OWL une fois
        g = ctx["reasoner"].reasoned_graph(ctx["base_g"], ctx["overlay_g"], freeze_ok=False, frozen_reasoner=False)

        # 2) rebuild mapping + traits + prey rules
        rebuild_species_mapping_and_rules(
            reasoned_g=g,
            active=ctx["state"].active,
            eats_cache=ctx["eats_cache"],
            base_g=ctx["base_g"],
            indiv_species=ctx["indiv_species"],
            species_traits=ctx["species_traits"],
            species_prey=ctx["species_prey"],
            known_species=ctx["state"].known_species,
        )

        # 3) init énergie manquante
        for u in list(ctx["state"].active):
            ctx["state"].energy.setdefault(u, ctx["state"].params["E_INIT"])

        # 4) edges affichage (one-time)
        auto_generate_eats_links_full(ctx["overlay_g"], ctx["state"].active, ctx["indiv_species"], ctx["species_prey"])

        # 5) init history t=0
        ctx["state"].history = {}
        pop0 = pop_by_species(ctx["state"].active, ctx["indiv_species"])
        for sp in set(list(pop0.keys())):
            ctx["state"].known_species.add(sp)
        for sp in ctx["state"].known_species:
            ctx["state"].history[sp] = [len(pop0.get(sp, []))]

        # 6) start
        ctx["state"].t = 0
        ctx["state"].frozen_reasoner = True
        ctx["state"].running = True

        return jsonify({"ok": True})

    @bp.post("/step")
    def api_step():
        if not ctx["state"].running:
            return jsonify({"ok": False})

        # wrappers lifecycle
        def create_individual(species_str: str):
            from simulation.lifecycle import create_individual as _create
            return _create(
                overlay_g=ctx["overlay_g"],
                active=ctx["state"].active,
                energy=ctx["state"].energy,
                params=ctx["state"].params,
                indiv_species=ctx["indiv_species"],
                known_species=ctx["state"].known_species,
                species_prey=ctx["species_prey"],
                species_str=species_str,
            )

        def remove_individual(u):
            from simulation.lifecycle import remove_individual as _remove
            return _remove(
                overlay_g=ctx["overlay_g"],
                active=ctx["state"].active,
                energy=ctx["state"].energy,
                indiv_species=ctx["indiv_species"],
                u=u,
            )

        simulation_step_energy(
            overlay_g=ctx["overlay_g"],
            active=ctx["state"].active,
            energy=ctx["state"].energy,
            params=ctx["state"].params,
            indiv_species=ctx["indiv_species"],
            species_traits=ctx["species_traits"],
            species_prey=ctx["species_prey"],
            create_individual_fn=create_individual,
            remove_individual_fn=remove_individual,
        )

        ctx["state"].t += 1

        status = update_history_and_check_stop(
            active=ctx["state"].active,
            indiv_species=ctx["indiv_species"],
            history=ctx["state"].history,
            known_species=ctx["state"].known_species,
            t=ctx["state"].t,
            params=ctx["state"].params,
        )

        if status:
            ctx["state"].running = False
            ctx["state"].frozen_reasoner = False

        ctx["reasoner"].mark_dirty()

        return jsonify({
            "ok": True,
            "t": ctx["state"].t,
            "status": status,
            "history": ctx["state"].history
        })

    return bp
