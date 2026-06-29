# Chronos CDK v0.2

**Emergent NPC Behavior + Theory Engine for Games**

Chronos is a physics-inspired engine that generates emergent NPC behavior without scripting, state machines, or behavior trees. NPCs develop personalities, form coalitions, elect leaders, remember events, and respond to player actions through pure field-driven computation.

As of v0.2, Chronos also includes the **Chronos-Metron theory engine**: symbolic theory generation with special mathematical constants (φ, π, e) and keyword-semantic operator evaluators.

## What Makes This Different?

| Traditional NPC AI | Chronos CDK |
|---|---|
| Behavior trees / state machines | Field-driven emergence |
| Scripted reactions | Personality + memory = unique responses |
| Static factions | Dynamic coalitions that form/break |
| No memory | NPCs remember kills, gifts, threats |
| Predictable | Every playthrough generates different behavior |

## Quick Start

```bash
# Clone the repo
git clone https://github.com/your-org/chronos-cdk.git
cd chronos-cdk

# Install dependencies
pip install -r requirements.txt

# Start the engine
python -m engine

# Open browser
# http://localhost:5000
```

## How It Works

1. **Engine computes fields** from game state (mood, intensity, operators)
2. **Each NPC's personality** interacts with fields differently
3. **Memory** modifies responses based on history (kills, gifts, time)
4. **Intent emerges** from the highest-scoring behavior
5. **Your client** polls the API and renders the NPCs

## API Overview

```bash
# Get NPC states (poll this every ~1 second)
GET http://localhost:5000/api/game/state

# Update player state
POST http://localhost:5000/api/arena/player
{
  "armed": true,
  "gift_active": false,
  "kills": 2,
  "x": 0.5,
  "y": 0.5
}
```

## NPC Emotions

Each NPC maintains 5 emotional states that influence behavior:

| Emotion | Range | Effect |
|---------|-------|--------|
| **trust** | -1 to +1 | Positive: curious/guard. Negative: attack |
| **fear** | 0 to 1 | High: flee. Decays over time |
| **anger** | 0 to 1 | High: attack. Builds from ally deaths |
| **loyalty** | 0 to 1 | High: follow leader, guard. Grows over time |
| **grief** | 0 to 1 | High: idle/orbit. Spikes on ally death |

## Narrative Events

The engine automatically generates named story events:

- **The Hunt** - 3+ NPCs enraged, hunting the player
- **The Succession** - Leadership changes within a coalition
- **The Alliance** - Two coalitions form an alliance
- **The Betrayal** - A coalition breaks an alliance

## Controls (Observatory Demo)

| Key | Action |
|-----|--------|
| WASD / Arrows | Move |
| Space | Toggle weapon |
| G | Give gift |

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed technical documentation.

## License

MIT - See [LICENSE](../LICENSE)
