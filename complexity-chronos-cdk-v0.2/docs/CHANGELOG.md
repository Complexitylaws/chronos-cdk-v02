# Changelog

## v0.2.0 (2026-06-29)

### Features
- **Chronos-Metron Theory Engine**: Symbolic theory generation with keyword-semantic operators
- **Special Mathematical Constants**: φ, π, e, √2, π/2, 1/φ, ln2 and negative variants
- **Keyword-Semantic Evaluator**: 80+ operator keywords matched to domain-appropriate behavior
- **Theory API**: New endpoints `/api/theory/domains`, `/api/theory/generate`, `/api/theory/evaluate`
- **Semantic Fitness Bonus**: Coherence and constants-context bonuses in theory evaluation

## v0.1.0 (2026-06-25)

### Features
- **Emergent NPC Intents**: 7 possible behaviors (attack, flee, guard, orbit, curious, scatter, idle) computed from field interactions
- **Personality Vectors**: 8 unique NPC personalities with aggression, curiosity, stability, social dimensions
- **Memory System**: NPCs remember kills, gifts, threats with emotional decay over time
- **Emotions**: trust, fear, anger, loyalty, grief per NPC
- **Emergent Leadership**: Per-coalition leader election based on social standing
- **Coalition Diplomacy**: Dynamic alliances and betrayals
- **Narrative Engine**: Auto-generated named story events (The Hunt, The Succession, The Alliance, The Betrayal)
- **Spatial Awareness**: Obstacle collision and avoidance
- **Flocking**: Coalition-based cohesion and separation
- **REST API**: Clean JSON endpoints for any client
- **Observatory Demo**: Full browser-based arena game demo
- **Minimal Client**: Single-file reference implementation

### Architecture
- Modular engine design (memory, intents, diplomacy, narrative)
- Configuration-driven personality and decay parameters
- Client-agnostic REST API (works with any engine/framework)
