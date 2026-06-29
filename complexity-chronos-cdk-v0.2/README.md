# Chronos CDK v0.2

**No scripting. No state machines. Pure field-driven emergence.**

Chronos is a physics-inspired NPC behavior engine that generates emergent gameplay through **field interactions**, **personality vectors**, and **memory systems**. Every playthrough is different because NPCs remember history and respond based on real-time field forces—not hardcoded conditions.

Perfect for game developers tired of behavior trees.

---

## The Big Difference

### Traditional AI ❌
```python
if player.armed:
    npc.state = "flee"
# Same behavior. Every time. Predictable.
```

### Chronos Emergence ✅
```python
threat_field = 0.78  # From: player armed + intensity + kills
aggression = npc.personality.aggression  # 0.2 to 0.9
score = threat_field * aggression
intent = argmax(scores)  # attack/flee/guard/orbit/curious/scatter/idle
# Different response. Every run. Emergent.
```

**Result:** 8 NPCs with the same personality react DIFFERENTLY to the same situation if they have different memories.

---

## Try It Now (2 minutes)

```bash
git clone https://github.com/Complexitylaws/chronos-cdk-v02
cd complexity-chronos-cdk-v0.2
pip install -r requirements.txt
python -m engine
```

Then open: **http://localhost:5000**

### Controls
- **WASD** - Move
- **Space** - Draw weapon (increases threat field)
- **G** - Offer gift (increases calm field)  
- **F** - Visualize fields (red = threat, green = calm)
- **?** - See why Chronos is different
- **Click NPC** - See exactly why they chose that behavior

---

## What You'll See

### Observatory Demo
A full interactive arena with 8 NPCs that:
- **React in real-time** to your actions
- **Form coalitions** (red/green/blue)
- **Remember kills & gifts** (emotions decay over time)
- **Generate story events** ("The Hunt", "The Succession", "The Betrayal")
- **Show exactly why they behave** (click any NPC to see the math)

### The 4 Fields (Interactive Visualization)
1. **Threat Field** (Red) - How dangerous the world feels
   - Increases: armed player, kills, chaos mood
   - Drives: attack, flee, scatter

2. **Calm Field** (Green) - How safe and stable
   - Increases: gifts, stable mood, coherence operators
   - Drives: guard, orbit, idle

3. **Curiosity Field** (Yellow) - How interesting
   - Increases: mysteries, pattern complexity, insight jumps
   - Drives: curious, orbit

4. **Orbit Field** (Cyan) - Pattern formation tendency
   - Increases: loop moods, self-reflection, coherence
   - Drives: orbit, guard

---

## How It Works

### Per Tick:
1. **Fields** computed from global game state
2. **Memory** updated (emotions decay, gifts processed)
3. **Intents scored** for each NPC: `field × personality × memory + noise`
4. **Leaders elected** per coalition
5. **Diplomacy** checked (alliances form/break)
6. **Story events** triggered (if thresholds met)
7. **All returned as JSON** → your game client polls

### The Math
```
intent_score = (
    field_value × personality_weight × multiplier +  
    memory_modifier +                                
    noise                                            
)

highest_score_wins = npc_intent
```

**Key insight:** Same NPC, different memory = different behavior. Always.

---

## 8 NPC Personalities (Pre-built)

Each NPC has:
- **Aggression** (0.0-1.0) - Prefer attack vs. flee
- **Curiosity** (0.0-1.0) - Drawn to interesting things
- **Stability** (0.0-1.0) - Stay calm under threat
- **Social** (0.0-1.0) - Form groups, follow leaders

Example:
- **A1**: Aggressive (0.8), Low Stability → Quick to attack, panics easily
- **A2**: Curious (0.8), High Stability → Investigates calmly
- **A3**: Social (0.9), High Stability → Natural leader, loyal

---

## Emergent Features (No Scripting)

### Emotions (Auto-decaying)
- **Trust** (-1.0 to +1.0) - Builds from gifts, degrades from kills
- **Fear** (0.0 to 1.0) - Builds from armed/kills, decays fast
- **Anger** (0.0 to 1.0) - Builds from ally death, decays slowly
- **Loyalty** (0.0 to 1.0) - Grows from shared faction
- **Grief** (0.0 to 1.0) - Spikes on death, decays very fast

### Coalitions (Dynamic)
- **Red** - Hostile to player
- **Green** - Friendly/allied
- **Blue** - Neutral/social
- Form/break based on average trust/anger between groups

### Story Events (Auto-generated)
- **The Hunt** - 3+ NPCs enraged, hunting player
- **The Succession** - Leader changes
- **The Alliance** - Two coalitions team up
- **The Betrayal** - Alliance breaks

---

## Integration (For Game Devs)

### REST API
Your game client polls one endpoint:

```javascript
GET http://localhost:5000/api/game/state
```

Returns:
```json
{
  "mood": "chaos",
  "intensity": 0.8,
  "npcs": {
    "A1": {
      "intent": "attack",
      "coalition": "red",
      "threat": 0.78,
      "trust": -0.5,
      "fear": 0.2,
      "anger": 0.9,
      "is_leader": true,
      "reason": "fields(threat=0.78) score=1.42"
    },
    ...
  },
  "narrative": [
    { "name": "The Hunt", "desc": "5 NPCs hunting player" }
  ]
}
```

### Update Player State
```javascript
POST http://localhost:5000/api/arena/player
{
  "armed": true,
  "gift_active": false,
  "kills": 2,
  "x": 0.5,
  "y": 0.5
}
```

See [docs/API.md](docs/API.md) for full reference.

### Client Examples
- **Python**: [examples/python_client.py](examples/python_client.py)
- **Unity C#**: [examples/unity_client.cs](examples/unity_client.cs)
- **Web**: Built-in Observatory demo

---

## Architecture

```
┌──────────────────────────┐
│   Game Client            │
│ (Unity/Godot/Web/Custom) │
└────────────┬─────────────┘
             │ REST API (JSON)
             ▼
┌──────────────────────────┐
│   Chronos Engine         │
├──────────────────────────┤
│ • Fields (threat, calm)  │
│ • Memory (emotions)      │
│ • Intent Scoring         │
│ • Diplomacy              │
│ • Narrative              │
└──────────────────────────┘
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for deep dive.

---

## Project Structure

```
complexity-chronos-cdk-v0.2/
├── engine/
│   ├── run.py                 # Flask server
│   ├── engine_core.py         # Main orchestrator
│   ├── engine_memory.py       # Emotions & decay
│   ├── engine_intents.py      # Field scoring
│   ├── engine_diplomacy.py    # Coalitions & leaders
│   ├── engine_narrative.py    # Story generation
│   ├── config.py              # All parameters (tunable)
│   ├── core/                  # Theory engine (v0.2)
│   ├── domains/               # Theory operators
│   └── evolution/             # Fitness functions
├── visualization/
│   └── observatory/           # Full demo UI (HTML/JS/CSS)
├── examples/
│   ├── python_client.py
│   └── unity_client.cs
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── CHANGELOG.md
│   └── README.md
├── requirements.txt
└── LICENSE
```

---

## Performance

- **Per-NPC per-tick**: ~1ms (CPU-bound)
- **8 NPCs @ 60Hz**: ~500KB/sec over HTTP
- **Scales to 100s of NPCs** with batching

---

## What's New in v0.2

- **Chronos-Metron Theory Engine** (experimental)
  - Symbolic theory generation
  - Special constants (φ, π, e, √2, ln2)
  - Keyword-semantic operators
  - Theory fitness evaluation
- **Theory API**: `/api/theory/generate`, `/api/theory/evaluate`
- **Observatory Enhancement**: Field visualization + NPC reasoning
- **Full documentation** (API, Architecture, examples)

---

## Roadmap (v0.3+)

- WebSocket support (reduce polling)
- Spatial awareness (obstacles, vision cones)
- Flocking behaviors (coalition coordination)
- Genetic algorithm for NPC generation
- More theory domains
- Unreal Engine plugin

---

## FAQ

### Why not just use behavior trees?
Behavior trees are great for **scripted** AI. Chronos is for **emergent** AI. Every playthrough generates different (but consistent) behavior because NPCs have memory and respond to field forces.

### Can I use this in commercial games?
**Yes.** MIT license. Free for everything.

### How do I customize NPC personalities?
Edit [engine/config.py](engine/config.py):
```python
NPC_PROFILES = [
    {"id": "A1", "aggression": 0.8, "curiosity": 0.3, ...},
    ...
]
```

### Can I add my own fields?
Yes. Modify `engine_intents.py` to compute new global fields and add them to intent scoring.

### Does it work with [my game engine]?
If it can make HTTP requests, yes. Examples: Unity, Godot, Unreal, custom engines. The engine is language-agnostic.

---

## License

MIT — Commercial and personal use allowed. See [LICENSE](LICENSE).

---

## Contact & Links

- **GitHub**: [@Complexitylaws](https://github.com/Complexitylaws)
- **Bluesky**: [@complexitylaws.bsky.social](https://bsky.app/profile/complexitylaws.bsky.social)
- **Email**: [complexitylaws@protonmail.com](mailto:complexitylaws@protonmail.com)

---

## Citation (if you use this)

```bibtex
@software{chronos_cdk_2026,
  title = {Chronos CDK: Physics-Inspired Emergent NPC Behavior Engine},
  author = {Complexitylaws},
  year = {2026},
  url = {https://github.com/Complexitylaws/chronos-cdk-v02}
}
```

---

**Made with ❤️ for game developers who want emergent AI, not scripts.**
