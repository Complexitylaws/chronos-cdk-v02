"""
Chronos CDK - Engine Core
==========================
The main engine orchestrator that ties together:
- Memory system (emotional state per NPC)
- Intent computation (field-driven behavior)
- Diplomacy (coalitions, leadership, alliances)
- Narrative (emergent story events)

This is a simplified physics simulation that generates
emergent NPC behavior without scripting or state machines.
"""

import time
import random
from .config import NPC_PROFILES, NICHE_MOOD_MAP, GIFT_DURATION
from .engine_memory import create_memory_store, update_memory
from .engine_intents import compute_npc_intents
from .engine_diplomacy import create_coalition_state, elect_leaders, update_diplomacy
from .engine_narrative import NarrativeEngine


class ChronosEngine:
    """
    The core Chronos NPC behavior engine.

    Usage:
        engine = ChronosEngine()
        engine.update_player_state(armed=True, gift_active=False, kills=0, x=0.5, y=0.5)
        state = engine.tick(mood="calm", intensity=0.3, operators=[], fitness=5.0, planck=False, depth=10)
    """

    def __init__(self):
        self.memory = create_memory_store()
        self.coalition_state = create_coalition_state()
        self.narrative = NarrativeEngine()
        self.player_state = {
            "x": 0.5,
            "y": 0.5,
            "armed": False,
            "gift_active": False,
            "gift_time": 0,
            "kills": 0,
        }
        self.messages = []
        self.tick_count = 0

    def update_player_state(self, armed=None, gift_active=None, kills=None, x=None, y=None):
        """Update player state from client."""
        if armed is not None:
            self.player_state["armed"] = bool(armed)
        if gift_active is not None:
            self.player_state["gift_active"] = bool(gift_active)
            if gift_active:
                self.player_state["gift_time"] = time.time()
        if kills is not None:
            self.player_state["kills"] = int(kills)
        if x is not None:
            self.player_state["x"] = float(x)
        if y is not None:
            self.player_state["y"] = float(y)

        # Auto-expire gift
        if time.time() - self.player_state.get("gift_time", 0) > GIFT_DURATION:
            self.player_state["gift_active"] = False

    def tick(self, mood="neutral", intensity=0.5, operators=None, fitness=0.0,
             planck=False, depth=0):
        """
        Run one engine tick. Returns complete game state dict.

        Parameters:
            mood:       Engine mood (calm, chaos, danger, loop, etc.)
            intensity:  How intense the current state is (0.0 - 1.0)
            operators:  List of active operator names
            fitness:    Current theory fitness score
            planck:     Whether planck limit is triggered
            depth:      Current theory depth
        """
        if operators is None:
            operators = []

        self.tick_count += 1

        # Auto-expire gift
        if time.time() - self.player_state.get("gift_time", 0) > GIFT_DURATION:
            self.player_state["gift_active"] = False

        # Update NPC memory
        narrative_events = []
        self.memory = update_memory(self.memory, self.player_state, narrative_events)

        # Add any new narrative events
        for ev in narrative_events:
            self.narrative.add_event(ev)

        # Compute NPC intents
        npcs, messages = compute_npc_intents(
            mood, intensity, operators, fitness, planck, depth,
            self.player_state, self.memory, self.coalition_state
        )

        # Run diplomacy and leadership
        diplomacy_events = []
        elect_leaders(npcs, self.memory, self.coalition_state, diplomacy_events)
        update_diplomacy(npcs, self.memory, self.coalition_state, diplomacy_events)
        for ev in diplomacy_events:
            self.narrative.add_event(ev)

        self.messages = messages

        return {
            "mood": mood,
            "intensity": intensity,
            "operators": operators,
            "fitness": fitness,
            "planck": planck,
            "depth": depth,
            "npcs": npcs,
            "messages": messages,
            "coalitions": self.coalition_state,
            "narrative": self.narrative.get_recent(5),
            "tick": self.tick_count,
        }

    def get_state_summary(self):
        """Get a compact summary of current engine state."""
        return {
            "player": self.player_state,
            "coalition_state": self.coalition_state,
            "narrative_count": len(self.narrative.events),
            "tick": self.tick_count,
        }
