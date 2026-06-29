"""
Chronos CDK - Theory Generator
==============================
Generates theory trees with special mathematical constants.
"""

import random
from .types import TheoryNode, Theory
from ..domains.domain_manager import DomainManager


OPERATORS = ["add", "mul", "sub", "div", "sin", "tanh", "sigmoid", "diff", "integrate", "max", "min"]
CONST_RANGE = (-3.0, 3.0)

SPECIAL_CONSTANTS = {
    "pi":    3.14159265,
    "phi":   1.61803398,
    "e":     2.71828182,
    "sqrt2": 1.41421356,
    "pi_2":  1.57079632,
    "inv_phi": 0.61803398,
    "ln2":   0.69314718,
    "neg_phi": -1.61803398,
    "neg_pi":  -3.14159265,
}
SPECIAL_CONST_PROB = 0.12
_SPECIAL_ITEMS = list(SPECIAL_CONSTANTS.items())


def _random_constant():
    """12% chance for a special constant, otherwise random float."""
    if random.random() < SPECIAL_CONST_PROB:
        name, val = random.choice(_SPECIAL_ITEMS)
        return TheoryNode(node_type="constant", value=val, const_label=name)
    return TheoryNode(node_type="constant", value=round(random.uniform(*CONST_RANGE), 3))


def generate_random_node(depth=0, max_depth=5):
    if depth >= max_depth or random.random() < 0.25:
        return _random_constant()
    op = random.choice(OPERATORS)
    node = TheoryNode(operator=op)
    if op in ["sin", "tanh", "sigmoid"]:
        node.children = [generate_random_node(depth + 1, max_depth)]
    else:
        num_children = random.randint(2, 4)
        node.children = [generate_random_node(depth + 1, max_depth) for _ in range(num_children)]
    return node


def generate_domain_node(domain, depth=0, max_depth=5):
    """Generate a node using a domain's operator set."""
    dm = DomainManager(domain)
    ops = dm.operator_names()
    if not ops:
        return generate_random_node(depth, max_depth)
    if depth >= max_depth or random.random() < 0.25:
        return _random_constant()
    op = random.choice(ops)
    arity = dm.arity(op)
    node = TheoryNode(operator=op)
    if arity == 0:
        node.children = []
    elif arity == 1:
        node.children = [generate_domain_node(domain, depth + 1, max_depth)]
    else:
        node.children = [generate_domain_node(domain, depth + 1, max_depth) for _ in range(arity)]
    return node


def generate_theory(domain="npc", max_depth=5):
    """Generate a full theory."""
    theory = Theory()
    if domain and domain != "generic":
        theory.root = generate_domain_node(domain, max_depth=random.randint(2, max_depth))
        theory.metadata["domain"] = domain
    else:
        theory.root = generate_random_node()
        theory.metadata["domain"] = "generic"
    theory.metadata["depth"] = get_depth(theory.root)
    theory.metadata["node_count"] = count_nodes(theory.root)
    return theory


def get_depth(node):
    if not node or not node.children:
        return 0
    return 1 + max((get_depth(c) for c in node.children), default=0)


def count_nodes(node):
    if not node:
        return 0
    return 1 + sum(count_nodes(c) for c in node.children)


def mutate_node(node, mutation_rate=0.25):
    if random.random() < mutation_rate:
        if node.node_type == "constant":
            c = _random_constant()
            node.value = c.value
            node.const_label = c.const_label
        else:
            node.operator = random.choice(OPERATORS)
    for child in node.children:
        mutate_node(child, mutation_rate)
    return node
