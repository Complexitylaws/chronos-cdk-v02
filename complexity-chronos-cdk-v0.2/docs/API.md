# Chronos CDK - API Documentation

## Base URL

```
http://localhost:5000
```

---

## GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "uptime": 142,
  "timestamp": "2026-06-25T18:00:00.000000"
}
```

---

## GET /api/game/state

**The main endpoint.** Returns complete engine state including all NPC intents, emotions, coalitions, and narrative events.

Poll this every 500ms-2000ms depending on your game's needs.

**Response:**
```json
{
  "mood": "calm",
  "intensity": 0.3,
  "fitness": 7.329,
  "niche": "Vaste Attractor",
  "operators": ["COHERENCE_FORMATION", "PATTERN_STABILITY"],
  "depth": 42,
  "planck": false,
  "planck_score": 0.0,
  "generation": 50,
  "discoveries": 968,
  "running": true,
  "timestamp": "2026-06-25T18:00:00.000000",
  "tick": 142,

  "npcs": {
    "A1": {
      "intent": "attack",
      "coalition": "red",
      "mood_local": "aggressive",
      "threat": 0.624,
      "trust": -0.4,
      "fear": 0.15,
      "anger": 0.82,
      "loyalty": 0.35,
      "grief": 0.12,
      "is_leader": false,
      "reason": "fields(threat=0.78,player_armed) score=1.42"
    },
    "A2": {
      "intent": "curious",
      "coalition": "green",
      "mood_local": "interested",
      "threat": 0.156,
      "trust": 0.6,
      "fear": 0.0,
      "anger": 0.0,
      "loyalty": 0.45,
      "grief": 0.0,
      "is_leader": true,
      "reason": "fields(calm=0.50,curiosity=0.60) score=1.28"
    }
  },

  "messages": [
    {"from": "A1", "to": "A4", "type": "warn", "content": "danger_nearby"},
    {"from": "A3", "to": "A6", "type": "coordinate", "content": "form_guard"}
  ],

  "coalitions": {
    "red": {"leader": "A1", "allies": [], "enemies": ["green"], "members": ["A1", "A5"]},
    "green": {"leader": "A2", "allies": ["blue"], "enemies": [], "members": ["A2", "A3", "A7"]},
    "blue": {"leader": "A6", "allies": ["green"], "enemies": [], "members": ["A4", "A6", "A8"]}
  },

  "narrative": [
    {"type": "hunt", "name": "The Hunt", "desc": "5 NPCs are enraged - hunting the player", "time": 1719334800.0},
    {"type": "leadership_change", "name": "The Succession", "desc": "A2 takes leadership of green from A6", "time": 1719334805.0}
  ]
}
```

### NPC Intent Values

| Intent | Meaning | Triggered By |
|--------|---------|------|
| `attack` | Moving toward player aggressively | High threat + high aggression |
| `flee` | Running away from player | High fear + low stability |
| `guard` | Forming protective formation | High calm + high stability |
| `orbit` | Circling at medium distance | Loop/complex mood + low aggression |
| `curious` | Approaching cautiously | High curiosity field + trust |
| `scatter` | Moving erratically | Noise spike + low stability |
| `idle` | Staying put | No dominant field |

### Coalition Values

| Coalition | Meaning |
|-----------|---------|
| `red` | Hostile to player |
| `green` | Allied/friendly to player |
| `blue` | Neutral/social |
| `neutral` | Undecided |

---

## POST /api/arena/player

Update player state. Call this when the player's state changes.

**Body:**
```json
{
  "armed": true,
  "gift_active": false,
  "kills": 2,
  "x": 0.5,
  "y": 0.5
}
```

| Field | Type | Description |
|-------|------|-------------|
| `armed` | bool | Is the player's weapon drawn? Increases threat field |
| `gift_active` | bool | Is the player offering a gift? Reduces threat, builds trust |
| `kills` | int | Total NPCs killed this session. Increases fear/anger/grief |
| `x` | float | Player X position (0.0 - 1.0 normalized) |
| `y` | float | Player Y position (0.0 - 1.0 normalized) |

**Response:**
```json
{"ok": true}
```

---

## POST /api/arena/event

Post a specific game event to the engine.

**Body:**
```json
{
  "type": "kill",
  "target": "A3",
  "data": {}
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Event type: `kill`, `gift`, `respawn` |
| `target` | string | NPC ID affected (e.g. "A1") |
| `data` | object | Additional event data (optional) |

**Response:**
```json
{"ok": true, "event": "kill"}
```

---

## Integration Guide

### Polling Pattern (Recommended)

```python
import requests
import time

while True:
    # 1. Send player state
    requests.post("http://localhost:5000/api/arena/player", json={
        "armed": player.is_armed,
        "gift_active": player.is_gifting,
        "kills": player.kill_count,
        "x": player.x / world_width,
        "y": player.y / world_height,
    })

    # 2. Get NPC intents
    state = requests.get("http://localhost:5000/api/game/state").json()

    # 3. Apply intents to your NPCs
    for npc_id, npc_data in state["npcs"].items():
        your_npc = find_npc(npc_id)
        your_npc.set_behavior(npc_data["intent"])
        your_npc.set_coalition(npc_data["coalition"])

    time.sleep(1.0)
```

---

## GET /api/theory/domains

List available theory domains.

**Response:**
```json
{"domains": ["npc"]}
```

---

## GET /api/theory/generate

Generate a random theory tree using keyword-semantic operators and special constants.

**Query params:**
- `domain`: str — theory domain (default: `npc`)
- `depth`: int — max tree depth (default: `4`)

**Response:**
```json
{
  "theory": {
    "id": "...",
    "root": {
      "type": "operator",
      "operator": "EMOTIONAL_DRIFT",
      "value": null,
      "const_label": null,
      "children": [...]
    },
    "metadata": {"domain": "npc", "depth": 3, "node_count": 5},
    "fitness": 1.0445
  },
  "fitness": 1.0445,
  "special_constants": ["pi", "phi", "e", "sqrt2", "pi_2", "inv_phi", "ln2", "neg_phi", "neg_pi"]
}
```

---

## POST /api/theory/evaluate

Evaluate a theory tree provided as JSON.

**Body:**
```json
{
  "domain": "npc",
  "theory": {
    "root": { ... }
  }
}
```

**Response:**
```json
{
  "ok": true,
  "domain": "npc",
  "root_value": 0.423,
  "fitness": 1.0445
}
```

### WebSocket (Future)

WebSocket support is planned for v0.2 to reduce polling overhead.
