"""
Chronos CDK - Python Client Example
=====================================
Minimal example showing how to integrate Chronos into your Python game.

Requirements:
    pip install requests

Usage:
    1. Start the Chronos engine: python -m engine
    2. Run this script: python examples/python_client.py
"""

import requests
import time

API_BASE = "http://localhost:5000"


def main():
    print("Chronos CDK - Python Client Example")
    print("=" * 40)
    print(f"Connecting to engine at {API_BASE}...")
    print()

    # Check engine health
    try:
        health = requests.get(f"{API_BASE}/api/health").json()
        print(f"Engine: {health['status']} (v{health['version']})")
    except requests.ConnectionError:
        print("ERROR: Engine not running. Start with: python -m engine")
        return

    # Simulate a game session
    print("\n--- Simulation: Peaceful start ---")
    requests.post(f"{API_BASE}/api/arena/player", json={
        "armed": False,
        "gift_active": False,
        "kills": 0,
        "x": 0.5,
        "y": 0.5,
    })
    time.sleep(1)
    state = requests.get(f"{API_BASE}/api/game/state").json()
    print_npcs(state)

    print("\n--- Simulation: Player draws weapon ---")
    requests.post(f"{API_BASE}/api/arena/player", json={
        "armed": True,
        "gift_active": False,
        "kills": 0,
        "x": 0.5,
        "y": 0.5,
    })
    time.sleep(1)
    state = requests.get(f"{API_BASE}/api/game/state").json()
    print_npcs(state)

    print("\n--- Simulation: Player kills 2 NPCs ---")
    requests.post(f"{API_BASE}/api/arena/player", json={
        "armed": True,
        "gift_active": False,
        "kills": 2,
        "x": 0.5,
        "y": 0.5,
    })
    time.sleep(1)
    state = requests.get(f"{API_BASE}/api/game/state").json()
    print_npcs(state)

    print("\n--- Simulation: Player offers gift ---")
    requests.post(f"{API_BASE}/api/arena/player", json={
        "armed": False,
        "gift_active": True,
        "kills": 0,
        "x": 0.5,
        "y": 0.5,
    })
    time.sleep(1)
    state = requests.get(f"{API_BASE}/api/game/state").json()
    print_npcs(state)

    # Print narrative events
    if state.get("narrative"):
        print("\n--- Narrative Events ---")
        for ev in state["narrative"]:
            print(f"  [{ev['name']}] {ev['desc']}")

    # Print coalitions
    print("\n--- Coalitions ---")
    for name, coal in state.get("coalitions", {}).items():
        if coal.get("members"):
            leader = coal.get("leader", "none")
            print(f"  {name}: leader={leader}, members={coal['members']}")


def print_npcs(state):
    """Print NPC states in a readable format."""
    for npc_id, npc in state.get("npcs", {}).items():
        leader = " [LEADER]" if npc.get("is_leader") else ""
        emotions = f"trust={npc['trust']:.1f} fear={npc['fear']:.1f} anger={npc['anger']:.1f}"
        print(f"  {npc_id}: {npc['intent']:8s} [{npc['coalition']:7s}] {emotions}{leader}")


if __name__ == "__main__":
    main()
