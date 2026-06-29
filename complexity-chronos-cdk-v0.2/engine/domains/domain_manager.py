"""
Chronos CDK - Domain Manager
============================
Keyword-semantic evaluator for domain operators.
"""

import json
import math
import random
import types
from collections import Counter
from pathlib import Path


DOMAINS_DIR = Path(__file__).parent


class DomainManager:
    def __init__(self, domain: str = "npc"):
        self.domain = domain
        config_path = DOMAINS_DIR / f"operators_{domain}.json"
        if not config_path.exists():
            self._config = {"operators": []}
            self._ops = {}
            return
        with open(config_path, "r", encoding="utf-8") as f:
            self._config = json.load(f)
        self._ops = {op["name"]: op for op in self._config["operators"]}

    def operator_names(self) -> list:
        return list(self._ops.keys())

    def arity(self, name: str) -> int:
        return self._ops.get(name, {}).get("arity", 1)

    def has_evaluator(self) -> bool:
        return len(self._ops) > 0

    def evaluate(self, op_name: str, args: list) -> float:
        if not hasattr(self, '_evaluator'):
            self._evaluator = self._build_evaluator()
        if self._evaluator is None:
            return 0.0
        return self._evaluator.evaluate(op_name, args)

    def _build_evaluator(self):
        op_names = list(self._ops.keys())

        KEYWORD_FUNCTIONS = [
            # Wave / oscillation
            ("WAVE",           lambda a: math.sin(a[0]) if a else 0.0),
            ("OSCILLAT",       lambda a: math.sin(a[0]) if a else 0.0),
            ("PHASE",          lambda a: math.cos(a[0]) if a else 0.0),
            ("RESONAN",        lambda a: math.sin(a[0]) * math.cos(a[1]) if len(a) > 1 else math.sin(a[0]) if a else 0.0),
            ("SIN",            lambda a: math.sin(a[0]) if a else 0.0),
            ("COS",            lambda a: math.cos(a[0]) if a else 0.0),
            ("TANH",           lambda a: math.tanh(a[0]) if a else 0.0),
            ("SIGMOID",        lambda a: 1.0 / (1.0 + math.exp(-a[0])) if a else 0.5),

            # Memory / state / feedback
            ("MEMORY",         lambda a: a[0] * 0.9 if a else 0.0),
            ("IMPRINT",        lambda a: a[0] * 0.85 if a else 0.0),
            ("FEEDBACK",       lambda a: a[0] - a[1] if len(a) > 1 else 0.0),
            ("STATE",          lambda a: math.tanh(a[0]) if a else 0.0),
            ("DECAY",          lambda a: a[0] * 0.8 if a else 0.0),
            ("DRIFT",          lambda a: a[0] * 0.95 if a else 0.0),
            ("INTEGRATE",      lambda a: sum(a) / max(1, len(a)) if a else 0.0),
            ("DIFF",           lambda a: a[0] - a[1] if len(a) > 1 else 0.0),
            ("ACCUMULAT",      lambda a: sum(a) if a else 0.0),
            ("HISTORY",        lambda a: a[0] * 0.9 if a else 0.0),
            ("TRACE",          lambda a: a[0] * 0.7 if a else 0.0),

            # Decision / threshold
            ("THRESHOLD",      lambda a: 1.0 if a and a[0] > 0 else 0.0),
            ("DECISION",       lambda a: 1.0 if a and a[0] > 0 else 0.0),
            ("GATE",           lambda a: 1.0 if a and a[0] > 0 else 0.0),
            ("BOUNDARY",       lambda a: 1.0 if a and abs(a[0]) < 1.0 else 0.0),
            ("CRITICAL",       lambda a: 1.0 if a and abs(a[0]) > 1.0 else 0.0),

            # Adaptation / learning
            ("ADAPT",          lambda a: a[0] + 0.1 * (a[1] - a[0]) if len(a) > 1 else a[0] if a else 0.0),
            ("LEARNING",       lambda a: a[0] + 0.1 * (a[1] - a[0]) if len(a) > 1 else a[0] if a else 0.0),
            ("REINFORC",       lambda a: a[0] + 0.2 * a[1] if len(a) > 1 else a[0] if a else 0.0),
            ("STRATEGY",       lambda a: max(0.0, a[0]) if a else 0.0),
            ("MUTATION",       lambda a: a[0] * (1.0 + 0.2 * (random.random() - 0.5)) if a else 0.0),
            ("VARIATION",      lambda a: a[0] * (1.0 + 0.2 * (random.random() - 0.5)) if a else 0.0),

            # Selection / fitness / evolution
            ("SELECT",         lambda a: max(a) if a else 0.0),
            ("FITNESS",        lambda a: sum(a) / max(1, len(a)) if a else 0.0),
            ("PRESSURE",       lambda a: a[0] * (1.0 + 0.2 * sum(a[1:])) if a else 0.0),
            ("SURVIVAL",       lambda a: max(0.0, a[0]) if a else 0.0),
            ("REPLICATION",    lambda a: a[0] * 2.0 if a else 0.0),
            ("GENERATION",     lambda a: a[0] * 1.1 if a else 0.0),
            ("EXTINCTION",     lambda a: 0.0 if a and a[0] < 0 else a[0] if a else 0.0),

            # Coherence / stability / emergence
            ("COHERENCE",      lambda a: math.tanh(sum(a) / max(1, len(a))) if a else 0.0),
            ("STABILITY",      lambda a: 1.0 / (1.0 + abs(a[0])) if a else 1.0),
            ("STABIL",         lambda a: 1.0 / (1.0 + abs(a[0])) if a else 1.0),
            ("EMERG",          lambda a: math.tanh(sum(x * x for x in a)) if a else 0.0),
            ("SELF_ORGAN",     lambda a: math.tanh(sum(x * x for x in a)) if a else 0.0),
            ("SYNERGY",        lambda a: sum(a) * (1.0 + 0.1 * len(a)) if a else 0.0),
            ("ALIGNMENT",      lambda a: a[0] * a[1] if len(a) > 1 else a[0] if a else 0.0),
            ("PATTERN",        lambda a: math.sin(sum(a)) if a else 0.0),
            ("STRUCTURE",      lambda a: abs(sum(a)) if a else 0.0),
            ("FORMATION",      lambda a: math.tanh(sum(a)) if a else 0.0),
            ("COUPLED",        lambda a: a[0] * a[1] if len(a) > 1 else a[0] if a else 0.0),
            ("BINDING",        lambda a: a[0] * a[1] if len(a) > 1 else a[0] if a else 0.0),
            ("NETWORK",        lambda a: sum(a) / max(1, len(a)) if a else 0.0),
            ("TOPOLOGY",       lambda a: math.tanh(sum(a)) if a else 0.0),
            ("PERSISTENCE",    lambda a: a[0] * (1.0 - 0.1 * len(a)) if a else 0.0),

            # Energy / force / field / potential
            ("ENERGY",         lambda a: sum(abs(x) for x in a) if a else 0.0),
            ("FORCE",          lambda a: a[0] * (1.0 + 0.2 * len(a)) if a else 0.0),
            ("POTENTIAL",      lambda a: a[0] * (1.0 - math.exp(-abs(a[0]))) if a else 0.0),
            ("FIELD",          lambda a: sum(a) / max(1, len(a)) if a else 0.0),
            ("GRADIENT",       lambda a: a[0] - a[1] if len(a) > 1 else a[0] if a else 0.0),
            ("PROPAGAT",       lambda a: a[0] * a[1] if len(a) > 1 else a[0] if a else 0.0),
            ("FLOW",           lambda a: sum(a) if a else 0.0),
            ("FLUX",           lambda a: a[0] * (1.0 + 0.1 * sum(a[1:])) if a else 0.0),
            ("DRIVE",          lambda a: math.tanh(sum(a)) if a else 0.0),
            ("MOTIVATION",     lambda a: math.tanh(sum(a)) if a else 0.0),
            ("IMPULSE",        lambda a: a[0] * math.exp(-abs(a[0])) if a else 0.0),
            ("STRESS",         lambda a: abs(a[0]) if a else 0.0),
            ("PRESS",          lambda a: abs(a[0]) if a else 0.0),

            # Entropy / information / noise
            ("ENTROPY",        lambda a: -sum(abs(x) * math.log1p(abs(x)) for x in a) / max(1, len(a)) if a else 0.0),
            ("INFORMATION",    lambda a: sum(abs(x) for x in a) if a else 0.0),
            ("NOISE",          lambda a: random.uniform(-1.0, 1.0) if a else 0.0),
            ("PERTURB",        lambda a: a[0] + random.uniform(-0.2, 0.2) if a else 0.0),
            ("JUNCTION",       lambda a: 1.0 / (1.0 + math.exp(-a[0])) if a else 0.5),
            ("CONSTRAIN",      lambda a: min(1.0, max(-1.0, a[0])) if a else 0.0),
            ("FILTER",         lambda a: a[0] if a and abs(a[0]) > 0.1 else 0.0),
            ("SMOOTH",         lambda a: sum(a) / max(1, len(a)) if a else 0.0),

            # Social / cognitive / NPC
            ("COGNITIVE",      lambda a: math.tanh(sum(a)) if a else 0.0),
            ("INTENTION",      lambda a: a[0] * (1.0 + 0.2 * len(a)) if a else 0.0),
            ("TRUST",          lambda a: math.tanh(sum(a)) if a else 0.0),
            ("THREAT",         lambda a: max(0.0, a[0]) if a else 0.0),
            ("EMOTION",        lambda a: math.tanh(a[0]) if a else 0.0),
            ("SOCIAL",         lambda a: sum(a) / max(1, len(a)) if a else 0.0),
            ("COALITION",      lambda a: math.tanh(sum(a)) if a else 0.0),
            ("NARRATIVE",      lambda a: a[0] * (1.0 + 0.1 * len(a)) if a else 0.0),
            ("IDENTITY",       lambda a: a[0] * (1.0 - 0.1 * len(a)) if a else 0.0),
            ("PERSONALITY",    lambda a: math.tanh(sum(x * x for x in a)) if a else 0.0),
            ("RECOVERY",       lambda a: a[0] * (1.0 - math.exp(-abs(a[0]))) if a else 0.0),
            ("TRAUMA",         lambda a: a[0] * math.exp(-abs(a[0])) if a else 0.0),
            ("EXPERIENCE",     lambda a: a[0] * 0.9 if a else 0.0),
            ("BEHAVIORAL",     lambda a: a[0] + random.uniform(-0.1, 0.1) if a else 0.0),
            ("DECISION_NOISE", lambda a: a[0] * (1.0 + 0.2 * random.uniform(-1.0, 1.0)) if a else 0.0),

            # Space / cosmology / gravity
            ("HAWKING",        lambda a: a[0] * (1.0 - math.exp(-abs(a[0]))) if a else 0.0),
            ("BEKENSTEIN",     lambda a: a[0] * math.log1p(abs(a[0])) if a else 0.0),
            ("SCHWARZSCHILD",  lambda a: -abs(a[0]) if a else 0.0),
            ("SCHWARZ",        lambda a: -abs(a[0]) if a else 0.0),
            ("TIDAL",          lambda a: a[0] * a[1] if len(a) > 1 else a[0] if a else 0.0),
            ("UNRUH",          lambda a: a[0] * (1.0 + 0.1 * abs(a[0])) if a else 0.0),
            ("WHEELER",        lambda a: a[0] * math.exp(-abs(a[0])) if a else 0.0),
            ("DEWITT",         lambda a: a[0] * math.exp(-abs(a[0])) if a else 0.0),
            ("KLEIN",          lambda a: math.sin(a[0]) if a else 0.0),
            ("GORDON",         lambda a: math.cos(a[0]) if a else 0.0),
            ("V_GRAV",         lambda a: a[0] * a[1] / (1.0 + a[1] * a[1]) if len(a) > 1 else a[0] if a else 0.0),
            ("V_ESC",          lambda a: math.sqrt(abs(a[0])) if a else 0.0),
            ("T_ORB",          lambda a: a[0] * math.sin(a[1]) if len(a) > 1 else a[0] if a else 0.0),
            ("DS_INTERVAL",    lambda a: a[0] / (1.0 + abs(a[0])) if a else 0.0),
            ("INTERVAL",       lambda a: a[0] / (1.0 + abs(a[0])) if a else 0.0),
            ("CASIMIR",        lambda a: -1.0 / (1.0 + abs(a[0])) if a else 0.0),
            ("HUBBLE",         lambda a: a[0] * (1.0 + 0.1 * len(a)) if a else 0.0),
            ("REDSHIFT",       lambda a: a[0] / (1.0 + abs(a[0])) if a else 0.0),
            ("DARK_ENERGY",    lambda a: a[0] if a else 0.0),
            ("FRIEDMANN",      lambda a: math.sqrt(abs(a[0])) if a else 0.0),
            ("PLANCK",         lambda a: abs(a[0]) / (1.0 + abs(a[0])) if a else 0.0),
            ("GEODESIC",       lambda a: a[0] * (1.0 - 0.1 * abs(a[0])) if a else 0.0),
            ("LORENTZ",        lambda a: 1.0 / math.sqrt(1.0 + a[0] * a[0]) if a else 1.0),
            ("YUKAWA",         lambda a: a[0] * math.exp(-abs(a[1])) if len(a) > 1 else a[0] if a else 0.0),
            ("COULOMB",        lambda a: a[0] / (1.0 + a[1] * a[1]) if len(a) > 1 else a[0] if a else 0.0),
            ("MASS",           lambda a: abs(a[0]) if a else 0.0),
            ("CHARGE",         lambda a: a[0] if a else 0.0),
            ("ORBIT",          lambda a: a[0] * math.sin(a[1]) if len(a) > 1 else a[0] if a else 0.0),
            ("SCALE",          lambda a: a[0] * (1.0 + 0.1 * len(a)) if a else 0.0),
            ("COMOVING",       lambda a: a[0] if a else 0.0),
            ("METRIC",         lambda a: 1.0 / (1.0 + abs(a[0])) if a else 0.0),
            ("CURVATURE",      lambda a: a[0] / (1.0 + abs(a[0])) if a else 0.0),
            ("EXPANSION",      lambda a: a[0] * (1.0 + 0.1 * len(a)) if a else 0.0),
            ("CONTRACT",       lambda a: a[0] * (1.0 - 0.1 * len(a)) if a else 0.0),
            ("DOPPLER",        lambda a: a[0] * (1.0 + 0.1 * a[1]) if len(a) > 1 else a[0] if a else 0.0),
            ("ESCAPE",         lambda a: math.sqrt(abs(a[0])) if a else 0.0),
            ("GRAVITATIONAL",  lambda a: a[0] * a[1] / (1.0 + a[1] * a[1]) if len(a) > 1 else a[0] if a else 0.0),
            ("TENSOR",         lambda a: math.tanh(sum(a)) if a else 0.0),

            # Math primitives
            ("ADD",            lambda a: sum(a) if a else 0.0),
            ("MUL",            lambda a: a[0] * a[1] if len(a) > 1 else a[0] if a else 0.0),
            ("SUB",            lambda a: a[0] - a[1] if len(a) > 1 else a[0] if a else 0.0),
            ("DIV",            lambda a: a[0] / (1e-6 + a[1]) if len(a) > 1 and a[1] != 0 else a[0] if a else 0.0),
            ("MAX",            lambda a: max(a) if a else 0.0),
            ("MIN",            lambda a: min(a) if a else 0.0),
            ("ABS",            lambda a: abs(a[0]) if a else 0.0),
            ("SQRT",           lambda a: math.sqrt(abs(a[0])) if a else 0.0),
            ("EXP",            lambda a: math.exp(max(-5.0, min(5.0, a[0]))) if a else 1.0),
            ("LOG",            lambda a: math.log1p(abs(a[0])) if a else 0.0),
            ("POW",            lambda a: a[0] ** (a[1] if len(a) > 1 else 1.0) if a else 0.0),
            ("NEG",            lambda a: -a[0] if a else 0.0),
            ("INV",            lambda a: 1.0 / (1e-6 + a[0]) if a and a[0] != 0 else 0.0),
            ("PRODUCT",        lambda a: math.prod(a) if a else 1.0),
            ("SUM",            lambda a: sum(a) if a else 0.0),
            ("MEAN",           lambda a: sum(a) / max(1, len(a)) if a else 0.0),
            ("VARIANCE",       lambda a: (sum((x - sum(a)/len(a))**2 for x in a) / len(a)) if a else 0.0),
        ]

        keyword_hit_counter = Counter()

        def _safe(x):
            try:
                if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
                    return 0.0
                return float(max(min(x, 1e6), -1e6))
            except Exception:
                return 0.0

        def _generic_eval(vals):
            s, m, v = sum(vals), max(vals), sum(abs(a) for a in vals)
            return _safe(0.4 * s + 0.3 * m + 0.3 * v)

        def _resolve(op_name):
            op_upper = op_name.upper()
            for kw, fn in KEYWORD_FUNCTIONS:
                if kw in op_upper:
                    return kw, fn
            return None, None

        RESOLVED = {op: _resolve(op) for op in op_names}

        def evaluate(op_name: str, args: list) -> float:
            kw, fn = RESOLVED.get(op_name, (None, None))
            vals = [_safe(a) for a in args] if args else [0.0]
            try:
                if fn is not None:
                    keyword_hit_counter[kw] += 1
                    return _safe(fn(vals))
                return _generic_eval(vals)
            except Exception:
                return _generic_eval(vals)

        mod = types.ModuleType(f"auto_eval_{self.domain}")
        mod.evaluate = evaluate
        mod.RESOLVED = RESOLVED
        mod.keyword_hit_counter = keyword_hit_counter
        mod._is_auto = True
        return mod
