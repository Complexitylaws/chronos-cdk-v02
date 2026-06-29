"""
Chronos CDK - Intent Computation Engine
=========================================
Pure field-driven intent computation.
No lookup tables. No state machines.

Each NPC's intent emerges from the interaction between:
- Engine field state (mood, intensity, operators)
- NPC personality weights (aggression, curiosity, stability, social)
- Player state (armed, gift, position, kills)
- NPC memory (trust, fear, anger, grief, loyalty)

Possible intents: attack, flee, guard, orbit, curious, scatter, idle
"""

import time
import hashlib
from .config import (
    NPC_PROFILES, THREAT_ARMED_BONUS, THREAT_KILL_WEIGHT, THREAT_KILL_CAP,
    GIFT_THREAT_MULTIPLIER, GIFT_CALM_BONUS, GIFT_CURIOSITY_BONUS, TRAUMA_DURATION
)


def compute_fields(mood, intensity, operators, player_state, planck):
    """
    Compute global field values from engine state.
    Returns: threat_field, calm_field, curiosity_field, orbit_field
    """
    ops_set = set(operators)

    # Threat field: how dangerous the world feels (0..1)
    threat_field = intensity * 0.5
    if mood in ("chaos", "danger"):
        threat_field += 0.35
    elif mood in ("fragment",):
        threat_field += 0.2
    if "NOISE_SPIKE" in ops_set:
        threat_field += 0.15
    if "FAILURE_PROPAGATION" in ops_set:
        threat_field += 0.1
    if planck:
        threat_field = min(threat_field + 0.4, 1.0)
    if player_state["armed"]:
        threat_field += THREAT_ARMED_BONUS

    # Kills increase threat (gift overrides)
    kills = player_state.get("kills", 0)
    if kills > 0 and not player_state["gift_active"]:
        threat_field += min(kills * THREAT_KILL_WEIGHT, THREAT_KILL_CAP)

    # Gift pacifies
    if player_state["gift_active"]:
        threat_field *= GIFT_THREAT_MULTIPLIER
    threat_field = min(max(threat_field, 0.0), 1.0)

    # Calm field: how stable/safe the world feels (0..1)
    calm_field = 0.0
    if mood in ("calm", "stable"):
        calm_field += 0.5
    elif mood in ("loop", "pulse"):
        calm_field += 0.3
    if "FEEDBACK_LOOP" in ops_set:
        calm_field += 0.2
    if "PATTERN_STABILITY" in ops_set:
        calm_field += 0.15
    if "NOISE_FILTER" in ops_set:
        calm_field += 0.1
    if player_state["gift_active"]:
        calm_field += GIFT_CALM_BONUS
    calm_field = min(max(calm_field, 0.0), 1.0)

    # Curiosity field: how interesting the world is (0..1)
    curiosity_field = 0.0
    if mood in ("rising", "complex"):
        curiosity_field += 0.3
    elif mood in ("loop",):
        curiosity_field += 0.2
    if "DRIFT_ATTENTION" in ops_set:
        curiosity_field += 0.2
    if "INSIGHT_JUMP" in ops_set:
        curiosity_field += 0.15
    if "EMERGENT_IDEA" in ops_set:
        curiosity_field += 0.1
    if player_state["gift_active"]:
        curiosity_field += GIFT_CURIOSITY_BONUS
    curiosity_field = min(max(curiosity_field, 0.0), 1.0)

    # Orbit field: tendency to form patterns (0..1)
    orbit_field = 0.0
    if mood in ("loop", "complex", "pulse"):
        orbit_field += 0.4
    if "SELF_REFLECT" in ops_set:
        orbit_field += 0.15
    if "COHERENCE_FORMATION" in ops_set:
        orbit_field += 0.2
    orbit_field = min(max(orbit_field, 0.0), 1.0)

    return threat_field, calm_field, curiosity_field, orbit_field


def compute_npc_intents(mood, intensity, operators, fitness, planck, depth,
                        player_state, memory, coalition_state):
    """
    Compute intent for each NPC based on fields, personality, and memory.
    Returns dict of NPC outputs and list of inter-NPC messages.
    """
    ops_set = set(operators)
    threat_field, calm_field, curiosity_field, orbit_field = compute_fields(
        mood, intensity, operators, player_state, planck
    )

    npcs_out = {}
    messages = []

    for prof in NPC_PROFILES:
        npc_id = prof["id"]
        agg = prof["aggression"]
        cur = prof["curiosity"]
        stab = prof["stability"]
        soc = prof["social"]

        # Deterministic per-NPC noise from engine state
        _seed = hashlib.md5(f"{npc_id}{depth}{int(fitness*1000)}".encode()).digest()
        noise = [((b % 100) / 100.0 - 0.5) * 0.25 for b in _seed[:7]]

        # Score each possible intent
        scores = {
            "attack":  threat_field * agg * 2.0 + noise[0],
            "flee":    threat_field * (1.0 - stab) * 1.6 + noise[1],
            "guard":   calm_field * stab * 1.2 + threat_field * soc * 0.4 + noise[2],
            "orbit":   (orbit_field + calm_field * 0.3) * (1.0 - agg) * 1.4 + noise[3],
            "curious": curiosity_field * cur * 2.0 + noise[4],
            "scatter": threat_field * (1.0 - stab) * 1.0 + (0.25 if "NOISE_SPIKE" in ops_set else 0) + noise[5],
            "idle":    (1.0 - threat_field) * (1.0 - curiosity_field) * (1.0 - calm_field) * 0.8 + noise[6],
        }

        # Memory modifies scores
        mem = memory[npc_id]
        scores["flee"] += mem["fear"] * 0.8
        scores["flee"] += mem["grief"] * 0.5
        scores["attack"] += max(0, -mem["trust"]) * 0.5
        scores["attack"] += mem["anger"] * 0.9
        scores["curious"] += max(0, mem["trust"]) * 0.6
        scores["guard"] += max(0, mem["trust"]) * 0.3
        scores["guard"] += mem["loyalty"] * 0.4
        scores["orbit"] += mem["grief"] * 0.3
        scores["idle"] += mem["grief"] * 0.4

        # Leadership: leaders prefer guard/attack, followers mirror leader
        if mem["is_leader"]:
            scores["guard"] += 0.3 * soc
            scores["attack"] += 0.2 * agg
        else:
            for coal_name, cs in coalition_state.items():
                if cs.get("leader") and npc_id in cs.get("members", []):
                    leader_id = cs["leader"]
                    if leader_id != npc_id and leader_id in memory:
                        leader_intent = memory[leader_id]["last_intent"]
                        scores[leader_intent] = scores.get(leader_intent, 0) + mem["loyalty"] * 0.5
                    break

        # Trauma response from ally death
        if time.time() - mem["ally_killed_at"] < TRAUMA_DURATION:
            trauma = 1.0 - ((time.time() - mem["ally_killed_at"]) / TRAUMA_DURATION)
            scores["flee"] += trauma * 0.6 * (1.0 - stab)
            scores["attack"] += trauma * 0.5 * agg
            scores["guard"] += trauma * 0.3 * soc

        # Clamp negatives
        scores = {k: max(v, 0.0) for k, v in scores.items()}

        # Planck override
        if planck:
            scores["flee"] += 1.5

        # Pick highest scoring intent
        intent = max(scores, key=scores.get)
        score_val = scores[intent]

        # Coalition assignment from field interaction
        coalition = "neutral"
        red_score = agg * threat_field * 2.0
        green_score = (stab * calm_field + cur * curiosity_field) * 1.5
        blue_score = soc * 0.8 + orbit_field * 0.5

        if player_state["gift_active"] and cur > 0.3:
            green_score += 0.5

        if red_score > green_score and red_score > blue_score and red_score > 0.4:
            coalition = "red"
        elif green_score > red_score and green_score > blue_score and green_score > 0.4:
            coalition = "green"
        elif blue_score > 0.3:
            coalition = "blue"

        # Reason string
        field_parts = []
        if threat_field > 0.5:
            field_parts.append(f"threat={threat_field:.2f}")
        if calm_field > 0.3:
            field_parts.append(f"calm={calm_field:.2f}")
        if curiosity_field > 0.3:
            field_parts.append(f"curiosity={curiosity_field:.2f}")
        if orbit_field > 0.3:
            field_parts.append(f"orbit={orbit_field:.2f}")
        if player_state["armed"]:
            field_parts.append("player_armed")
        if player_state["gift_active"]:
            field_parts.append("gift_active")
        reason = f"fields({','.join(field_parts)}) score={score_val:.2f}"

        # Local mood
        if threat_field > calm_field and threat_field > curiosity_field:
            mood_local = "tense" if intent != "attack" else "aggressive"
        elif curiosity_field > calm_field:
            mood_local = "interested"
        elif calm_field > 0.3:
            mood_local = "relaxed"
        else:
            mood_local = "neutral"

        mem["last_intent"] = intent
        npcs_out[npc_id] = {
            "intent": intent,
            "coalition": coalition,
            "mood_local": mood_local,
            "threat": round(threat_field * agg, 3),
            "trust": round(mem["trust"], 2),
            "fear": round(mem["fear"], 2),
            "anger": round(mem["anger"], 2),
            "loyalty": round(mem["loyalty"], 2),
            "grief": round(mem["grief"], 2),
            "is_leader": mem["is_leader"],
            "reason": reason,
        }

    # Generate inter-NPC messages
    npc_list = list(npcs_out.items())
    for i, (id_a, a) in enumerate(npc_list):
        for j, (id_b, b) in enumerate(npc_list):
            if i >= j:
                continue
            if a["intent"] == "flee" and b["intent"] == "idle":
                messages.append({"from": id_a, "to": id_b, "type": "warn", "content": "danger_nearby"})
            if a["coalition"] == b["coalition"] and a["intent"] == "guard" and b["intent"] != "guard":
                messages.append({"from": id_a, "to": id_b, "type": "coordinate", "content": "form_guard"})
            if a["intent"] == "curious" and b["coalition"] == a["coalition"]:
                messages.append({"from": id_a, "to": id_b, "type": "share", "content": "something_interesting"})

    return npcs_out, messages
