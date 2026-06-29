"""
Chronos CDK - Theory Fitness
=============================
Computes fitness for theory trees, including semantic coherence and
special constants bonus.
"""

import math
from ..core.generate import SPECIAL_CONSTANTS
from ..domains.domain_manager import DomainManager


def compute_domain_bonus(theory, domain="npc", weight=1.2):
    """
    Evaluate a theory tree using keyword-semantic operators.
    Returns a score with semantic coherence and constants bonus.
    """
    if theory.root is None:
        return 0.0

    dm = DomainManager(domain)
    if not dm.has_evaluator():
        return 0.0

    op_names = set(dm.operator_names())
    scores = []
    used_ops = set()

    special_consts = set(SPECIAL_CONSTANTS.keys())
    const_hits = 0

    def walk(node):
        nonlocal const_hits
        if node is None:
            return 0.0
        child_vals = [walk(c) for c in node.children]
        if node.node_type == "constant":
            if node.const_label and node.const_label in special_consts:
                const_hits += 1
            return float(node.value or 0.0)
        op = getattr(node, "operator", None)
        if op and op in op_names:
            args = child_vals if child_vals else [0.0]
            val = dm.evaluate(op, args)
            if not (math.isnan(val) or math.isinf(val)):
                scores.append(val)
                used_ops.add(op)
            return val
        return float(child_vals[0]) if child_vals else 0.0

    walk(theory.root)

    if not scores:
        return 0.0

    mean_abs = sum(abs(s) for s in scores) / len(scores)
    mean_val = sum(scores) / len(scores)
    variance = sum((s - mean_val) ** 2 for s in scores) / len(scores)
    richness = math.tanh(mean_abs) * math.tanh(math.sqrt(variance + 1e-6))
    diversity = math.tanh(len(used_ops) / 3.0)
    depth = theory.metadata.get("depth", 0)
    depth_bonus = min(depth * 0.08, 0.48)

    semantic_coherence = 0.0
    try:
        ev = dm._build_evaluator()
        if hasattr(ev, "RESOLVED"):
            total = len(used_ops)
            matched = sum(1 for op in used_ops if ev.RESOLVED.get(op, (None, None))[0] is not None)
            if total > 0:
                semantic_coherence = matched / total
    except Exception:
        semantic_coherence = 0.0

    const_fit_bonus = min(const_hits * 0.05, 0.15)
    sem_bonus = min(semantic_coherence + const_fit_bonus, 0.40)

    total = weight * (0.5 * richness + 0.3 * diversity + 0.2) + depth_bonus + sem_bonus
    theory.metadata["semantic_coherence"] = round(semantic_coherence, 4)
    theory.metadata["const_bonus"] = round(const_fit_bonus, 4)
    return round(total, 4)
