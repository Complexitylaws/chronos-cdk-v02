"""
Chronos CDK v0.2 - Main Server
================================
Flask API server that exposes:
  - The Chronos NPC behavior engine
  - The Chronos-Metron theory engine (special constants + semantic evaluators)

Start:
    python -m engine.run

Endpoints:
    GET  /                      -> Observatory demo UI
    GET  /api/game/state        -> Full engine state + NPC intents
    POST /api/arena/player      -> Update player state
    GET  /api/health            -> Health check
    GET  /api/theory/domains    -> List theory domains
    GET  /api/theory/generate   -> Generate a theory
    POST /api/theory/evaluate   -> Evaluate a theory tree
"""

import time
import math
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, request, render_template
from .engine_core import ChronosEngine
from .config import HOST, PORT, DEBUG, NICHE_MOOD_MAP
from .core.generate import generate_theory, SPECIAL_CONSTANTS
from .domains.domain_manager import DomainManager
from .evolution.fitness import compute_domain_bonus

app = Flask(
    __name__,
    template_folder="../visualization/observatory",
    static_folder="../visualization/observatory/assets",
)

# Initialize engine
engine = ChronosEngine()

# Simulated engine state (in production, connect to your physics engine)
_sim_state = {
    "niche": "Topologische Lus",
    "fitness": 5.0,
    "depth": 10,
    "generation": 1,
    "discoveries": 0,
    "planck": False,
    "planck_score": 0.0,
    "operators": ["COHERENCE_FORMATION", "PATTERN_STABILITY"],
}


@app.route("/")
def index():
    """Serve the Observatory demo UI."""
    return render_template("index.html")


@app.route("/api/health")
def api_health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "version": "0.1.0",
        "uptime": engine.tick_count,
        "timestamp": datetime.now().isoformat(),
    })


@app.route("/api/arena/player", methods=["POST"])
def api_arena_player():
    """
    Receive player state from client.

    Body (JSON):
        armed:       bool  - Is weapon drawn?
        gift_active: bool  - Is gift being offered?
        kills:       int   - Total NPC kills this session
        x:           float - Player X position (0.0 - 1.0)
        y:           float - Player Y position (0.0 - 1.0)
    """
    try:
        data = request.json or {}
        engine.update_player_state(
            armed=data.get("armed"),
            gift_active=data.get("gift_active"),
            kills=data.get("kills"),
            x=data.get("x"),
            y=data.get("y"),
        )
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.route("/api/game/state")
def api_game_state():
    """
    Get complete engine state including NPC intents.

    This is the main endpoint your game client should poll.
    Returns NPC intents, emotions, coalitions, and narrative events.
    """
    try:
        # Map niche to mood
        mood_data = NICHE_MOOD_MAP.get(
            _sim_state["niche"],
            {"mood": "neutral", "intensity": 0.5}
        )

        # Run engine tick
        state = engine.tick(
            mood=mood_data["mood"],
            intensity=mood_data["intensity"],
            operators=_sim_state["operators"],
            fitness=_sim_state["fitness"],
            planck=_sim_state["planck"],
            depth=_sim_state["depth"],
        )

        # Add metadata
        state["niche"] = _sim_state["niche"]
        state["generation"] = _sim_state["generation"]
        state["discoveries"] = _sim_state["discoveries"]
        state["planck_score"] = _sim_state["planck_score"]
        state["domain_bonus"] = 0.0
        state["running"] = True
        state["timestamp"] = datetime.now().isoformat()

        return jsonify(state)

    except Exception as e:
        return jsonify({
            "error": str(e),
            "mood": "neutral",
            "intensity": 0.5,
            "npcs": {},
            "messages": [],
            "running": False,
            "timestamp": datetime.now().isoformat(),
        }), 500


@app.route("/api/arena/event", methods=["POST"])
def api_arena_event():
    """
    Post a game event to the engine.

    Body (JSON):
        type:    str - Event type (kill, gift, respawn, etc.)
        target:  str - NPC id affected (e.g. "A1")
        data:    dict - Additional event data
    """
    try:
        data = request.json or {}
        event_type = data.get("type", "unknown")
        target = data.get("target")

        if event_type == "kill" and target and target in engine.memory:
            engine.memory[target]["ally_killed_at"] = time.time()

        return jsonify({"ok": True, "event": event_type})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


# ── Theory Engine Helpers ───────────────────────────────────────────────────

def _evaluate_theory_tree(node, domain_mgr):
    """Recursively evaluate a TheoryNode using domain operators."""
    if node is None:
        return 0.0
    child_vals = [_evaluate_theory_tree(c, domain_mgr) for c in node.children]
    if node.node_type == "constant":
        return float(node.value or 0.0)
    op = getattr(node, "operator", None)
    if op and op in domain_mgr._ops:
        args = child_vals if child_vals else [0.0]
        val = domain_mgr.evaluate(op, args)
        return 0.0 if (math.isnan(val) or math.isinf(val)) else val
    return float(child_vals[0]) if child_vals else 0.0


def _node_from_dict(data):
    """Rebuild a TheoryNode from JSON dict."""
    from .core.types import TheoryNode
    node = TheoryNode(
        id=data.get("id", "n/a"),
        node_type=data.get("type", "operator"),
        operator=data.get("operator", "add"),
        value=data.get("value"),
        const_label=data.get("const_label"),
    )
    node.children = [_node_from_dict(c) for c in data.get("children", [])]
    return node


@app.route("/api/theory/domains")
def api_theory_domains():
    """List available theory domains."""
    domains = [p.stem.replace("operators_", "") for p in (Path(__file__).parent / "domains").glob("operators_*.json")]
    return jsonify({"domains": domains})


@app.route("/api/theory/generate")
def api_theory_generate():
    """
    Generate a random theory tree.

    Query params:
        domain: str  - Domain to use (default: npc)
        depth:  int  - Max depth (default: 4)
    """
    try:
        domain = request.args.get("domain", "npc")
        depth = int(request.args.get("depth", 4))
        theory = generate_theory(domain=domain, max_depth=depth)
        fitness = compute_domain_bonus(theory, domain=domain)
        theory.fitness = fitness
        return jsonify({
            "theory": theory.to_dict(),
            "fitness": fitness,
            "special_constants": list(SPECIAL_CONSTANTS.keys()),
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.route("/api/theory/evaluate", methods=["POST"])
def api_theory_evaluate():
    """
    Evaluate a theory tree provided as JSON.

    Body (JSON):
        domain: str  - Domain to evaluate against
        theory: dict - TheoryNode tree (from /api/theory/generate)
    """
    try:
        data = request.json or {}
        domain = data.get("domain", "npc")
        theory_data = data.get("theory")
        if not theory_data or not theory_data.get("root"):
            return jsonify({"ok": False, "error": "missing theory.root"}), 400

        dm = DomainManager(domain)
        root = _node_from_dict(theory_data["root"])
        root_value = _evaluate_theory_tree(root, dm)
        fitness = compute_domain_bonus(_make_theory(root, theory_data.get("metadata", {})), domain=domain)

        return jsonify({
            "ok": True,
            "domain": domain,
            "root_value": root_value,
            "fitness": fitness,
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


def _make_theory(root, metadata):
    """Build a Theory object from a root node and metadata."""
    from .core.types import Theory
    t = Theory(root=root)
    t.metadata.update(metadata)
    return t


def main():
    """Start the Chronos CDK server."""
    print(f"[Chronos CDK v0.2] Starting on http://{HOST}:{PORT}")
    print(f"[Chronos CDK v0.2] Observatory: http://localhost:{PORT}/")
    print(f"[Chronos CDK v0.2] API: http://localhost:{PORT}/api/game/state")
    print(f"[Chronos CDK v0.2] Theory API: http://localhost:{PORT}/api/theory/generate")
    app.run(host=HOST, port=PORT, debug=DEBUG)


if __name__ == "__main__":
    main()
