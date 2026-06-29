 Chronos CDK v0.2 — Client Development Kit
The Chronos CDK is a lightweight developer kit containing the NPC Engine, Theory Wrapper, Semantic Evaluator, and API Server used for emergent NPC behavior, theory generation, and real‑time simulation.

This repository contains the public CDK, not the private Chronos Core.
It is designed for developers who want to integrate Chronos‑style NPC behavior into games, simulations, or research environments.

 What’s Included (Public)
✔ NPC Domain
Intent scoring

Memory & emotion model

Diplomacy (coalitions, leadership)

Narrative event generation

✔ Theory Wrapper
Special constants (φ, π, e)

Tree generation (light version)

Keyword‑semantic operator evaluator

Semantic coherence scoring

✔ Evolution (Light)
Fitness scoring

Constant bonus

Domain‑specific evaluation

✔ API Server
REST endpoints for game clients:

Code
/api/game/state
/api/arena/player
/api/theory/generate
/api/theory/evaluate
✔ Visualization
Observatory (HTML/JS)

Minimal client

✔ Examples
Python client

Unity C# client

❗ What’s NOT Included (Private)
This CDK does not contain the private Chronos Core:

Attractor engine

Multi‑domain evolution

Stability engine

Multi‑scale memory

Physics / Autonomous / Resilience domains

Deep theory generator

Discovery engine

Domain fusion

Stability chains

φ‑attractor logic

These components remain private and are not part of this repository.

Quick Start
bash
# Clone
git clone https://github.com/Complexitylaws/chronos-cdk-v02.git
cd chronos-cdk-v02

# Install
pip install -r requirements.txt

# Run API server
python -m chronoscdk

# Open browser
http://localhost:5000
 Project Structure
Code
chronos-cdk-v02/
├── chronoscdk/
│   ├── engine_core.py
│   ├── engine_intents.py
│   ├── engine_memory.py
│   ├── engine_diplomacy.py
│   ├── engine_narrative.py
│   ├── run.py
│   ├── core/
│   ├── domains/
│   └── evolution/
├── docs/
├── examples/
├── visualization/
├── LICENSE
└── requirements.txt
📄 License
MIT — free for personal and commercial use.
The private Chronos Core is not included in this license.

💬 Contact
For questions, collaboration, or research inquiries:
Use GitHub Issues on this repository.
