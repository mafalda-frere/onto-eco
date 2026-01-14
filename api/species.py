from flask import Blueprint, jsonify

from ontology.species import list_species

def build_species_bp(ctx):
    bp = Blueprint("species", __name__)

    @bp.get("/species")
    def api_species():
        return jsonify(list_species(ctx["base_g"]))

    return bp
