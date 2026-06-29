"""
Chronos CDK - TheoryNode with special constants
===============================================
Theory tree nodes used for symbolic theory generation and evaluation.
"""

import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class TheoryNode:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    node_type: str = "operator"
    operator: str = "add"
    children: List["TheoryNode"] = field(default_factory=list)
    value: Optional[float] = None
    const_label: Optional[str] = None  # NEU: symboolnaam (φ, π, e, ...)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.node_type,
            "operator": self.operator,
            "value": self.value,
            "const_label": self.const_label,
            "children": [c.to_dict() for c in self.children]
        }

    def __repr__(self):
        if self.node_type == "constant":
            return f"{self.const_label or self.value}"
        return f"{self.operator}({', '.join(str(c) for c in self.children)})"


@dataclass
class Theory:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    root: Optional[TheoryNode] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    fitness: float = 0.0
    niche: str = "unknown"
    generation: int = 0
    parent_id: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "root": self.root.to_dict() if self.root else None,
            "metadata": self.metadata,
            "fitness": self.fitness,
            "niche": self.niche,
            "generation": self.generation,
            "parent_id": self.parent_id
        }
