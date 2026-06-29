"""
Chronos CDK - Coalition Diplomacy & Leadership
================================================
Emergent leadership election and coalition diplomacy.

Leadership: highest social * (1 - fear) * (0.5 + loyalty) becomes leader.
Diplomacy: alliances form on mutual trust, break on high anger.
"""

import time
from .config import NPC_PROFILES


def create_coalition_state():
    """Initialize coalition state."""
    return {
        "red": {"leader": None, "allies": [], "enemies": [], "members": []},
        "green": {"leader": None, "allies": [], "enemies": [], "members": []},
        "blue": {"leader": None, "allies": [], "enemies": [], "members": []},
        "neutral": {"leader": None, "allies": [], "enemies": [], "members": []},
    }


def elect_leaders(npcs_out, memory, coalition_state, narrative_events):
    """
    Emergent leader election per coalition.
    Leader = NPC with highest social * (1-fear) * (0.5 + loyalty)
    """
    coalitions = {}
    for npc_id, data in npcs_out.items():
        coal = data["coalition"]
        if coal not in coalitions:
            coalitions[coal] = []
        coalitions[coal].append(npc_id)

    for coal, members in coalitions.items():
        if not members:
            continue

        best_id, best_score = None, -1
        for npc_id in members:
            mem = memory[npc_id]
            prof = next(p for p in NPC_PROFILES if p["id"] == npc_id)
            score = prof["social"] * (1.0 - mem["fear"]) * (0.5 + mem["loyalty"])
            if score > best_score:
                best_score = score
                best_id = npc_id

        # Track leadership changes
        old_leader = coalition_state.get(coal, {}).get("leader")
        if coal not in coalition_state:
            coalition_state[coal] = {"leader": None, "allies": [], "enemies": [], "members": []}
        coalition_state[coal]["leader"] = best_id
        coalition_state[coal]["members"] = members

        # Mark in memory
        for npc_id in members:
            memory[npc_id]["is_leader"] = (npc_id == best_id)

        # Narrative: leadership change
        if old_leader and old_leader != best_id:
            narrative_events.append({
                "type": "leadership_change",
                "name": "The Succession",
                "desc": f"{best_id} takes leadership of {coal} from {old_leader}",
                "time": time.time(),
            })

    # Update is_leader in output
    for npc_id in npcs_out:
        npcs_out[npc_id]["is_leader"] = memory[npc_id]["is_leader"]


def update_diplomacy(npcs_out, memory, coalition_state, narrative_events):
    """
    Coalition diplomacy: alliances form on mutual trust, break on anger.
    """
    coalitions = list(set(d["coalition"] for d in npcs_out.values()))

    for i, coal_a in enumerate(coalitions):
        for coal_b in coalitions[i + 1:]:
            members_a = [nid for nid, d in npcs_out.items() if d["coalition"] == coal_a]
            members_b = [nid for nid, d in npcs_out.items() if d["coalition"] == coal_b]

            if not members_a or not members_b:
                continue

            avg_trust_a = sum(memory[m]["trust"] for m in members_a) / len(members_a)
            avg_trust_b = sum(memory[m]["trust"] for m in members_b) / len(members_b)

            # Alliance forms when both sides have positive trust
            if avg_trust_a > 0.3 and avg_trust_b > 0.3:
                cs_a = coalition_state.setdefault(coal_a, {"leader": None, "allies": [], "enemies": [], "members": []})
                cs_b = coalition_state.setdefault(coal_b, {"leader": None, "allies": [], "enemies": [], "members": []})
                if coal_b not in cs_a.get("allies", []):
                    cs_a["allies"].append(coal_b)
                    cs_b["allies"].append(coal_a)
                    if coal_b in cs_a.get("enemies", []):
                        cs_a["enemies"].remove(coal_b)
                    if coal_a in cs_b.get("enemies", []):
                        cs_b["enemies"].remove(coal_a)
                    narrative_events.append({
                        "type": "alliance",
                        "name": "The Alliance",
                        "desc": f"{coal_a} and {coal_b} form an alliance",
                        "time": time.time(),
                    })

            # Hostility when anger is high
            avg_anger_a = sum(memory[m]["anger"] for m in members_a) / len(members_a)
            if avg_anger_a > 0.5:
                cs_a = coalition_state.setdefault(coal_a, {"leader": None, "allies": [], "enemies": [], "members": []})
                if coal_b not in cs_a.get("enemies", []):
                    cs_a["enemies"].append(coal_b)
                    if coal_b in cs_a.get("allies", []):
                        cs_a["allies"].remove(coal_b)
                        narrative_events.append({
                            "type": "betrayal",
                            "name": "The Betrayal",
                            "desc": f"{coal_a} breaks alliance with {coal_b}",
                            "time": time.time(),
                        })
