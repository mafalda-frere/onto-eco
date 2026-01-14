from rdflib import Graph
from owlrl import DeductiveClosure, OWLRL_Semantics

class ReasonerCache:
    def __init__(self):
        self._cache = None
        self._dirty = True

    def mark_dirty(self) -> None:
        self._dirty = True

    def merged_graph_raw(self, base_g: Graph, overlay_g: Graph) -> Graph:
        g = Graph()
        for t in base_g:
            g.add(t)
        for t in overlay_g:
            g.add(t)
        return g

    def reasoned_graph(self, base_g: Graph, overlay_g: Graph, freeze_ok: bool, frozen_reasoner: bool) -> Graph:
        """
        - Pendant simu (freeze_ok=True + frozen_reasoner=True), on renvoie le cache.
        - Hors simu ou si dirty, on recalcule.
        """
        if freeze_ok and frozen_reasoner:
            if self._cache is None:
                g = self.merged_graph_raw(base_g, overlay_g)
                DeductiveClosure(OWLRL_Semantics).expand(g)
                self._cache = g
                self._dirty = False
            return self._cache

        if self._cache is not None and not self._dirty:
            return self._cache

        g = self.merged_graph_raw(base_g, overlay_g)
        DeductiveClosure(OWLRL_Semantics).expand(g)
        self._cache = g
        self._dirty = False
        return g
