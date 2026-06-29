"""
Chronos CDK - Configuration
============================
All tunable parameters in one place.
"""

# Server
HOST = "0.0.0.0"
PORT = 5000
DEBUG = False

# NPC Profiles - 8 distinct personality vectors
# Each NPC responds differently to the same field state
NPC_PROFILES = [
    {"id": "A1", "aggression": 0.8, "curiosity": 0.2, "stability": 0.3, "social": 0.4},  # aggressive hothead
    {"id": "A2", "aggression": 0.2, "curiosity": 0.8, "stability": 0.5, "social": 0.6},  # curious explorer
    {"id": "A3", "aggression": 0.5, "curiosity": 0.3, "stability": 0.9, "social": 0.7},  # stable guardian
    {"id": "A4", "aggression": 0.3, "curiosity": 0.6, "stability": 0.2, "social": 0.3},  # nervous scout
    {"id": "A5", "aggression": 0.7, "curiosity": 0.4, "stability": 0.6, "social": 0.2},  # lone wolf
    {"id": "A6", "aggression": 0.1, "curiosity": 0.7, "stability": 0.4, "social": 0.9},  # social butterfly
    {"id": "A7", "aggression": 0.6, "curiosity": 0.5, "stability": 0.7, "social": 0.5},  # balanced fighter
    {"id": "A8", "aggression": 0.4, "curiosity": 0.9, "stability": 0.3, "social": 0.8},  # eager follower
]

# Memory decay rates (per tick)
FEAR_DECAY = 0.995
ANGER_DECAY = 0.998
GRIEF_DECAY = 0.99
TRUST_DECAY = 0.998
LOYALTY_GROWTH = 0.001

# Gift effects
GIFT_TRUST_BOOST = 0.3
GIFT_FEAR_REDUCE = 0.4
GIFT_ANGER_REDUCE = 0.3
GIFT_GRIEF_REDUCE = 0.2
GIFT_DURATION = 3.0  # seconds

# Kill effects
KILL_FEAR_BOOST = 0.3
KILL_TRUST_REDUCE = 0.2
KILL_ANGER_BOOST = 0.4
KILL_GRIEF_BOOST = 0.5
KILL_LOYALTY_BOOST = 0.1  # death bonds survivors

# Field weights
THREAT_ARMED_BONUS = 0.25
THREAT_KILL_WEIGHT = 0.15
THREAT_KILL_CAP = 0.5
GIFT_THREAT_MULTIPLIER = 0.3
GIFT_CALM_BONUS = 0.3
GIFT_CURIOSITY_BONUS = 0.6

# Narrative thresholds
HUNT_ANGER_THRESHOLD = 0.5
HUNT_MIN_NPCS = 3
TRAUMA_DURATION = 15.0  # seconds

# Engine moods mapped from niche classification
NICHE_MOOD_MAP = {
    "Chaotisch":         {"mood": "chaos",    "intensity": 0.9},
    "Explosief":         {"mood": "danger",   "intensity": 1.0},
    "Vaste Attractor":   {"mood": "calm",     "intensity": 0.3},
    "Stabiele Structuur": {"mood": "stable",  "intensity": 0.2},
    "Topologische Lus":  {"mood": "loop",     "intensity": 0.6},
    "Oscillator":        {"mood": "pulse",    "intensity": 0.5},
    "Gefragmenteerd":    {"mood": "fragment", "intensity": 0.7},
    "Veelbelovend":      {"mood": "rising",   "intensity": 0.6},
    "Complexe Lussen":   {"mood": "complex",  "intensity": 0.8},
    "Transient":         {"mood": "shift",    "intensity": 0.4},
}
