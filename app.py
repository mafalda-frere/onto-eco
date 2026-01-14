import os
import random
from flask import Flask, send_from_directory

from config import ONTO_PATH, SIMULATION_PARAMS
from simulation.state import SimulationState

from ontology.loader import load_base_graph, new_overlay_graph
from ontology.reasoner import ReasonerCache
from ontology.species import EatsRulesCache

from api.species import build_species_bp
from api.state import build_state_bp
from api.simulation import build_simulation_bp


def create_app() -> Flask:
    app = Flask(__name__)

    # --- Load graphs ---
    base_g = load_base_graph(ONTO_PATH)
    overlay_g = new_overlay_graph()

    # --- Simulation state ---
    state = SimulationState(params=SIMULATION_PARAMS)

    # --- Caches & mappings ---
    reasoner = ReasonerCache()
    eats_cache = EatsRulesCache()

    indiv_species = {}   # URIRef -> species_str
    species_traits = {}  # species_str -> traits dict
    species_prey = {}    # pred_species_str -> [prey_species_str]

    # rng helper (stable format used in original code)
    def rng4():
        return random.randint(1000, 9999)

    # --- shared context dict (simple & explicite) ---
    ctx = {
        "base_g": base_g,
        "overlay_g": overlay_g,
        "state": state,
        "reasoner": reasoner,
        "eats_cache": eats_cache,
        "indiv_species": indiv_species,
        "species_traits": species_traits,
        "species_prey": species_prey,
        "rng": rng4,
    }

    # --- API blueprints ---
    api_prefix = "/api"
    app.register_blueprint(build_species_bp(ctx), url_prefix=api_prefix)
    app.register_blueprint(build_state_bp(ctx), url_prefix=api_prefix)
    app.register_blueprint(build_simulation_bp(ctx), url_prefix=api_prefix)

    # --- UI route ---
    @app.get("/")
    def index():
        # sert ecosystem/ui/index.html
        ui_dir = os.path.join(os.path.dirname(__file__), "ui")
        return send_from_directory(ui_dir, "index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
