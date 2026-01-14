from dataclasses import dataclass, field
from typing import Dict, Set, Any

@dataclass
class SimulationState:
    running: bool = False
    frozen_reasoner: bool = False
    t: int = 0

    history: Dict[str, list] = field(default_factory=dict)

    # ensembles/dicos "dynamiques"
    active: Set[Any] = field(default_factory=set)     # contient des URIRef
    energy: Dict[Any, int] = field(default_factory=dict)  # URIRef -> int
    known_species: Set[str] = field(default_factory=set)

    params: Dict[str, Any] = field(default_factory=dict)
