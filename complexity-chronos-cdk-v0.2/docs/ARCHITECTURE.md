# Chronos CDK - Architecture

## Overview

```
┌─────────────────────────────────────────────────────┐
│                   Game Client                        │
│  (Unity, Godot, Web, or any HTTP client)           │
└──────────────────────┬──────────────────────────────┘
                       │ REST API (JSON)
┌──────────────────────┴──────────────────────────────┐
│                 Chronos Engine                       │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │  Fields  │  │  Memory  │  │  Intent Scoring  │ │
│  │ (threat, │─>│ (trust,  │─>│  (per NPC per    │ │
│  │  calm,   │  │  fear,   │  │   possible       │ │
│  │  curiosi-│  │  anger,  │  │   behavior)      │ │
│  │  ty,     │  │  grief,  │  │                  │ │
│  │  orbit)  │  │  loyalty)│  └────────┬─────────┘ │
│  └──────────┘  └──────────┘           │            │
│                                       ▼            │
│  ┌──────────────┐  ┌─────────────────────────────┐│
│  │  Diplomacy   │  │  Winner = NPC Intent        ││
│  │  (alliances, │<─│  (attack/flee/guard/orbit/  ││
│  │   leaders,   │  │   curious/scatter/idle)     ││
│  │   betrayal)  │  └─────────────────────────────┘│
│  └──────┬───────┘                                  │
│         │                                          │
│  ┌──────┴───────┐                                  │
│  │  Narrative   │                                  │
│  │  (The Hunt,  │                                  │
│  │   Succession,│                                  │
│  │   Alliance,  │                                  │
│  │   Betrayal)  │                                  │
│  └──────────────┘                                  │
└─────────────────────────────────────────────────────┘
```

## Engine Layers

### 1. Field Computation (`engine_intents.py`)

The engine computes 4 global fields from game state:

| Field | Source | Range | Effect |
|-------|--------|-------|--------|
| **threat_field** | mood=chaos/danger, armed, kills, planck | 0-1 | Drives attack/flee |
| **calm_field** | mood=calm/stable, gift, stability ops | 0-1 | Drives guard/orbit |
| **curiosity_field** | mood=rising/complex, gift, insight ops | 0-1 | Drives curious |
| **orbit_field** | mood=loop/complex, coherence ops | 0-1 | Drives orbit |

### 2. Personality Vectors (`config.py`)

Each NPC has 4 personality dimensions:

| Dimension | Effect |
|-----------|--------|
| **aggression** | High: prefers attack. Low: prefers flee/orbit |
| **curiosity** | High: drawn to interesting things |
| **stability** | High: stays calm under threat. Low: panics |
| **social** | High: follows leaders, forms groups |

### 3. Memory System (`engine_memory.py`)

Each NPC maintains emotional state that **decays over time**:

```
trust:   builds from gifts, degrades from kills
fear:    builds from armed/kills, decays (half-life ~10s)
anger:   builds from ally death, decays slowly (~20s)
loyalty: grows over time, boosts from shared trauma
grief:   spikes on ally death, decays fast (~5s)
```

Memory creates **history-dependent** behavior. An NPC that saw you kill its ally will respond differently than one that didn't - even with identical personality vectors.

### 4. Intent Scoring

For each NPC, every possible intent gets a score:

```
score = field_value * personality_weight * multiplier + memory_modifier + noise
```

The highest-scoring intent wins. Noise ensures diversity even in uniform conditions.

### 5. Leadership (`engine_diplomacy.py`)

Per coalition, one NPC emerges as leader:

```
leadership_score = social * (1 - fear) * (0.5 + loyalty)
```

- Leaders prefer guard/attack
- Followers mirror their leader's intent (weighted by loyalty)
- Leader death triggers "The Succession" event

### 6. Diplomacy (`engine_diplomacy.py`)

Coalitions can form alliances or declare hostility:

- **Alliance**: Forms when average trust between coalitions > 0.3
- **Hostility**: Forms when average anger > 0.5
- **Betrayal**: Breaking an existing alliance (high anger overrides)

### 7. Narrative Engine (`engine_narrative.py`)

Automatically detects and names emergent patterns:

| Event | Trigger |
|-------|---------|
| The Hunt | 3+ NPCs with anger > 0.5 |
| The Succession | Leader changes |
| The Alliance | Two coalitions ally |
| The Betrayal | Alliance breaks |

## Data Flow (Per Tick)

1. Client POSTs player state
2. `update_memory()` - decay emotions, process kills/gifts
3. `compute_fields()` - calculate global threat/calm/curiosity/orbit
4. `compute_npc_intents()` - score each behavior per NPC
5. `elect_leaders()` - determine coalition leaders
6. `update_diplomacy()` - check for alliance/betrayal
7. Return full state as JSON

## Client Architecture

The client is intentionally simple:
- Polls API every ~1 second
- Renders NPCs based on intent (movement patterns)
- Sends player state on input change
- All intelligence lives server-side

This means you can swap the client for Unity, Godot, Unreal, or any framework that can make HTTP requests.
