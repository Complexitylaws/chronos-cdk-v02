"""
Chronos CDK - Narrative Engine
===============================
Automatically generates named story events from emergent patterns.

Events are NOT scripted - they emerge from NPC state transitions:
- "The Hunt"       - 3+ NPCs enraged, hunting the player
- "The Succession" - Leadership changes within a coalition
- "The Alliance"   - Two coalitions form an alliance
- "The Betrayal"   - A coalition breaks an alliance
"""

import time


class NarrativeEngine:
    """Manages narrative event generation and history."""

    def __init__(self, max_history=50):
        self.events = []
        self.max_history = max_history

    def add_event(self, event):
        """Add a narrative event. Deduplicates within 2 seconds."""
        now = time.time()
        # Prevent duplicate events within short timeframe
        for existing in self.events[-5:]:
            if (existing["name"] == event["name"] and
                    now - existing["time"] < 2.0):
                return
        self.events.append(event)
        if len(self.events) > self.max_history:
            self.events = self.events[-self.max_history:]

    def get_recent(self, count=5):
        """Get most recent narrative events."""
        return self.events[-count:] if self.events else []

    def clear(self):
        """Clear all narrative history."""
        self.events = []
