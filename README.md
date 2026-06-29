# Chronos CDK v0.2 — Emergent NPC Intelligence Engine

Chronos CDK v0.2 is the public-facing development kit for the Chronos 
NPC Intelligence Engine. It exposes the API layer, behavior modules, 
and the Observatory demo, while the private core (evolution kernel, 
attractor engine, stability logic) remains closed.

This CDK is intended for researchers, AI-engineers, and game-engine 
developers evaluating non-scripted, emergent NPC behavior.

---

## Why This Is Different

Chronos does not use behavior trees, GOAP, utility curves, or 
hand-authored scripts.

NPC behavior emerges from memory, intent dynamics, diplomacy, narrative 
pressure, and domain-driven evolution, exposed through a clean API.

The engine produces state trajectories and behavioral structures that 
are not explicitly programmed — only constrained.

---

## What the Engine Actually Finds

Chronos searches for behavioral structures under domain pressure.
Below is an example of a structure discovered during evolution
(domain: cosmic_ray_biological_impact, v0.2):

THRESHOLD_CROSSING_DYNAMICS( FEEDBACK_LOOP_RECONFIGURATION( FLUX_STRUCTURE_COUPLING(2.597, -1.61803398) ) ) fitness: 7.338


This structure was not programmed. It was found.

Evolutionary-discovered structures are statistically distinguishable 
from random formulas of equal complexity (p < 0.0001, bootstrap 
n=10,000, non-trivial trees n=1,110).

---

## Observatory Demo

The Observatory provides a real-time view of NPC behavior:

- Intent switching
- Coalition formation
- Emotional state changes
- Narrative events
- Player interaction
- Dynamic stability / instability

![Observatory Screenshot](docs/observatory_screenshot.png)

---

## Quick Start

Requires Python 3.10+

```bash
git clone https://github.com/Complexitylaws/chronos-cdk-v02
cd chronos-cdk-v02
pip install -r requirements.txt
python -m chronoscdk

Open: http://localhost:5000

You will see the live NPC arena.
API Overview

GET  /api/game/state
POST /api/arena/player
POST /api/theory/generate
POST /api/theory/evaluate

This allows external clients (Python, Unity, custom engines) to integrate Chronos NPC behavior directly.
Architecture

chronoscdk/
  engine_core.py
  engine_intents.py
  engine_memory.py
  engine_diplomacy.py
  engine_narrative.py
  core/
  domains/
  evolution/
visualization/observatory/
examples/
docs/

The private core is not included. The CDK provides the public modules required for integration and evaluation.
Examples

Python Client

python examples/python_client.py

Queries the engine, prints NPC state, and demonstrates basic interaction.

Unity C# Client A Unity C# template is included as a starting point for game engine integration.
Changelog

v0.2

    Added Observatory v2 (HTML/JS)
    Added full REST API endpoints
    Added domain manager and theory wrapper
    Added diplomacy and narrative modules
    Added special constants (φ, π, e) in evolution
    Added keyword-semantic operator evaluator
    Added Python client example
    Improved engine structure and module separation

License

MIT — free for personal and commercial use. The private Chronos Core is not included in this license.
Contact

For research inquiries or collaboration: GitHub Issues
email: complexitylaws@protonmail.com
https://bsky.app/profile/complexitylaws.bsky.social

