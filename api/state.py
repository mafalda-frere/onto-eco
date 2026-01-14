from flask import Blueprint, jsonify
from rdflib.namespace import RDF

from ontology.species import local_name
from ontology.loader import AWO1, AWO4, EATS

def build_state_bp(ctx):
    bp = Blueprint("state", __name__)

    def list_entities():
        g = ctx["reasoner"].reasoned_graph(
            ctx["base_g"], ctx["overlay_g"],
            freeze_ok=True,
            frozen_reasoner=ctx["state"].frozen_reasoner
        )
        entities = []
        for u in sorted(ctx["state"].active, key=lambda x: str(x)):
            types = set()
            for t in g.objects(u, RDF.type):
                ts = str(t)
                if ts.startswith(str(AWO1)) or ts.startswith(str(AWO4)):
                    if "#" in ts:
                        types.add(local_name(t))
            entities.append({
                "id": str(u),
                "types": sorted(types),
                "energy": ctx["state"].energy.get(u, None)
            })
        return entities

    def list_edges():
        edges = []
        for s, _, o in ctx["overlay_g"].triples((None, EATS, None)):
            if s in ctx["state"].active and o in ctx["state"].active:
                edges.append({"source": str(s), "target": str(o), "pred": "eats"})
        return edges

    @bp.get("/state")
    def api_state():
        return jsonify({"nodes": list_entities(), "edges": list_edges()})

    return bp
