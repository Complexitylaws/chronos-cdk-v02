"""
Chronos CDK - NPC Memory System
================================
Each NPC maintains emotional memory that decays over time.
Memories influence intent scoring, creating emergent behavior
based on HISTORY rather than just current state.

Emotions:
- trust:   -1 (hate) to +1 (love) - builds from gifts, degrades from kills
- fear:    0 to 1 - builds from armed player/kills, decays over time
- anger:   0 to 1 - builds from ally death, decays slowly
- loyalty: 0 to 1 - grows over time in same coalition
- grief:   0 to 1 - spikes on ally death, decays fast
"""

import time
from .config import (
    NPC_PROFILES, FEAR_DECAY, ANGER_DECAY, GRIEF_DECAY, TRUST_DECAY,
    LOYALTY_GROWTH, GIFT_TRUST_BOOST, GIFT_FEAR_REDUCE, GIFT_ANGER_REDUCE,
    GIFT_GRIEF_REDUCE, GIFT_DURATION, KILL_FEAR_BOOST, KILL_TRUST_REDUCE,
    KILL_ANGER_BOOST, KILL_GRIEF_BOOST, KILL_LOYALTY_BOOST,
    HUNT_ANGER_THRESHOLD, HUNT_MIN_NPCS
)


def create_memory_store():
    """Initialize memory for all NPCs."""
    memory = {}
    for prof in NPC_PROFILES:
        memory[prof["id"]] = {
            "ally_killed_at": 0,
            "gift_received_at": 0,
            "player_armed_since": 0,
            "times_attacked": 0,
            "trust": 0.0,
            "fear": 0.0,
            "anger": 0.0,
            "loyalty": 0.0,
            "grief": 0.0,
            "is_leader": False,
            "last_intent": "idle",
            "_last_kills": 0,
        }
    return memory


def update_memory(memory, player_state, narrative_events):
    """
    Update all NPC memories based on current player state.
    Called each game tick. Returns updated memory dict.
    """
    now = time.time()

    for prof in NPC_PROFILES:
        npc_id = prof["id"]
        mem = memory[npc_id]

        # Decay emotions over time
        mem["fear"] = max(0.0, mem["fear"] * FEAR_DECAY)
        mem["anger"] = max(0.0, mem["anger"] * ANGER_DECAY)
        mem["grief"] = max(0.0, mem["grief"] * GRIEF_DECAY)

        # Loyalty grows slowly (bonding over time)
        mem["loyalty"] = min(1.0, mem["loyalty"] + LOYALTY_GROWTH)

        # Trust drifts toward neutral
        if abs(mem["trust"]) > 0.01:
            mem["trust"] *= TRUST_DECAY

        # Player armed builds alertness
        if player_state.get("armed"):
            mem["player_armed_since"] += 1
            mem["fear"] = min(1.0, mem["fear"] + 0.01)
            mem["anger"] = min(1.0, mem["anger"] + 0.005)
        else:
            mem["player_armed_since"] = max(0, mem["player_armed_since"] - 2)

        # Gift builds trust, reduces negative emotions
        if player_state.get("gift_active"):
            time_since_gift = now - mem["gift_received_at"]
            if time_since_gift > 2.0:  # don't double-count same gift
                mem["gift_received_at"] = now
                mem["trust"] = min(1.0, mem["trust"] + GIFT_TRUST_BOOST)
                mem["fear"] = max(0.0, mem["fear"] - GIFT_FEAR_REDUCE)
                mem["anger"] = max(0.0, mem["anger"] - GIFT_ANGER_REDUCE)
                mem["grief"] = max(0.0, mem["grief"] - GIFT_GRIEF_REDUCE)

        # Kills build fear, anger, grief
        kills = player_state.get("kills", 0)
        if kills > mem.get("_last_kills", 0):
            new_kills = kills - mem["_last_kills"]
            mem["fear"] = min(1.0, mem["fear"] + new_kills * KILL_FEAR_BOOST)
            mem["trust"] = max(-1.0, mem["trust"] - new_kills * KILL_TRUST_REDUCE)
            mem["anger"] = min(1.0, mem["anger"] + new_kills * KILL_ANGER_BOOST)
            mem["grief"] = min(1.0, mem["grief"] + new_kills * KILL_GRIEF_BOOST)
            mem["loyalty"] = min(1.0, mem["loyalty"] + new_kills * KILL_LOYALTY_BOOST)
            mem["ally_killed_at"] = now

            # Narrative: The Hunt
            total_angry = sum(
                1 for p in NPC_PROFILES
                if memory[p["id"]]["anger"] > HUNT_ANGER_THRESHOLD
            )
            if total_angry >= HUNT_MIN_NPCS:
                narrative_events.append({
                    "type": "hunt",
                    "name": "The Hunt",
                    "desc": f"{total_angry} NPCs are enraged - hunting the player",
                    "time": now,
                })

        mem["_last_kills"] = kills

    return memory
