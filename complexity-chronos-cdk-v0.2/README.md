# Chronos CDK v0.2

**Emergent NPC Behavior + Theory Engine for Games**

Chronos is a physics-inspired engine that generates emergent NPC behavior without scripting, state machines, or behavior trees. NPCs develop personalities, form coalitions, elect leaders, remember events, and respond to player actions through pure field-driven computation.

As of v0.2, Chronos also includes the **Chronos-Metron theory engine**: symbolic theory generation with special mathematical constants (φ, π, e) and keyword-semantic operator evaluators.

---

## What's New in v0.2

- **Chronos-Metron Theory Engine**: symbolic theory trees with special mathematical constants (golden ratio φ, π, e, √2, ln2, etc.)
- **Keyword-Semantic Evaluator**: 80+ operator keywords mapped to domain-specific deterministic functions
- **Theory REST API**: generate and evaluate theories via HTTP
  - `GET /api/theory/generate`
  - `POST /api/theory/evaluate`
  - `GET /api/theory/domains`
- **Semantic Fitness Bonus**: rewards theories that use keyword-matched operators and special constants
- **NPC Domain Operators**: a starter set of emergent-cognition operators for NPC behavior research

---

## What Makes This Different?

| Traditional NPC AI | Chronos CDK |
|---|---|
| Behavior trees / state machines | Field-driven emergence |
| Scripted reactions | Personality + memory = unique responses |
| Static factions | Dynamic coalitions that form/break |
| No memory | NPCs remember kills, gifts, threats |
| Predictable | Every playthrough generates different behavior |

---

## Quick Start

```bash
# Clone
git clone https://github.com/your-org/chronos-cdk.git
cd chronos-cdk

# Install
pip install -r requirements.txt

# Run
python -m engine

# Open browser: http://localhost:5000
```

**Controls:** WASD = move, Space = toggle weapon, G = gift

---

## API (for your game client)

```bash
# Get all NPC states
curl http://localhost:5000/api/game/state

# Update player state
curl -X POST http://localhost:5000/api/arena/player \
  -H "Content-Type: application/json" \
  -d '{"armed": true, "gift_active": false, "kills": 0, "x": 0.5, "y": 0.5}'

# Generate a theory with special constants
curl "http://localhost:5000/api/theory/generate?domain=npc&depth=4"

# Evaluate a theory
curl -X POST http://localhost:5000/api/theory/evaluate \
  -H "Content-Type: application/json" \
  -d '{"domain": "npc", "theory": {"root": {...}}}'
```

See [docs/API.md](docs/API.md) for full documentation.

---

## Architecture

```
Client (Unity/Godot/Web)  <-->  REST API  <-->  Chronos Engine
                                                  |
                                    ┌─────────────┼─────────────┐
                                    |             |             |
                                 Fields       Memory      Diplomacy
                                 (threat,     (trust,     (leaders,
                                  calm,       fear,       alliances,
                                  curiosity)  anger)      betrayal)
                                    |             |             |
                                    └─────────────┼─────────────┘
                                                  |
                                           Intent Scoring
                                           (per NPC, per tick)
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

---

## Project Structure

```
chronos-cdk/
├── engine/                 # Core engine (Python)
│   ├── run.py             # Flask server + API
│   ├── engine_core.py     # Main orchestrator
│   ├── engine_memory.py   # NPC memory & emotions
│   ├── engine_intents.py  # Intent scoring
│   ├── engine_diplomacy.py # Leadership & alliances
│   ├── engine_narrative.py # Story event generation
│   ├── core/              # Chronos-Metron theory engine
│   │   ├── types.py       # TheoryNode with const_label
│   │   └── generate.py    # Special constants + theory generation
│   ├── domains/           # Domain operator configs
│   │   ├── domain_manager.py  # Keyword-semantic evaluator
│   │   └── operators_npc.json
│   ├── evolution/         # Theory fitness
│   │   └── fitness.py     # Semantic coherence + constants bonus
│   └── config.py          # All tunable parameters
├── visualization/
│   ├── observatory/       # Full demo client (HTML/JS)
│   └── minimal_client/    # Bare minimum client
├── examples/
│   ├── python_client.py   # Python integration example
│   └── unity_client.cs    # Unity C# integration example
├── docs/
│   ├── API.md            # Full API documentation
│   ├── ARCHITECTURE.md   # Technical architecture
│   └── CHANGELOG.md      # Version history
├── requirements.txt
└── LICENSE (MIT)
```

---

## License

MIT — free for both commercial and personal use. See [LICENSE](LICENSE).

---

## Contact

- Bluesky: [@complexitylaws.bsky.social](https://bsky.app/profile/complexitylaws.bsky.social)
- Email: [complexitylaws@protonmail.com](mailto:complexitylaws@protonmail.com)
