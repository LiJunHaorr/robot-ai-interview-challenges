from copy import deepcopy
from dataclasses import asdict

from .models import Effect, Event


class RobotApplication:
    """Pure event-driven reception policy; integrations consume returned effects."""

    def __init__(self, absence_timeout_s: float = 10.0):
        if absence_timeout_s < 0:
            raise ValueError("absence_timeout_s must be non-negative")
        self.absence_timeout_s = float(absence_timeout_s)
        self._people = {}
        self._conversation_active = False
        self._meeting_active = False
        self._last_timestamp = None

    def handle_event(self, event: Event) -> list[Effect]:
        if not isinstance(event, Event):
            raise TypeError("event must be an Event")
        if self._last_timestamp is not None and event.timestamp < self._last_timestamp:
            raise ValueError("events must be received in non-decreasing timestamp order")
        self._last_timestamp = event.timestamp
        if event.event_type == "PERSON_ENTERED":
            return self._entered(event)
        if event.event_type == "PERSON_LEFT":
            return self._left(event)
        if event.event_type in ("CONVERSATION_STARTED", "MEETING_STARTED"):
            self._set_interaction(event.event_type, True)
            return []
        if event.event_type in ("CONVERSATION_ENDED", "MEETING_ENDED"):
            self._set_interaction(event.event_type, False)
            return []
        if event.event_type == "TICK":
            return self._tick(event.timestamp)
        raise ValueError(f"unknown event type: {event.event_type}")

    def _set_interaction(self, event_type, active):
        if event_type.startswith("CONVERSATION"):
            self._conversation_active = active
        else:
            self._meeting_active = active

    def _suppressed(self):
        return self._conversation_active or self._meeting_active

    def _require_person(self, event):
        if not event.person_id:
            raise ValueError(f"{event.event_type} requires person_id")
        return self._people.setdefault(event.person_id, {
            "present": False, "welcomed": False, "left_at": None, "farewelled": False,
        })

    def _entered(self, event):
        state = self._require_person(event)
        if state["present"]:
            return []
        if state["left_at"] is not None and not state["farewelled"]:
            state["present"] = True
            state["left_at"] = None
            return []
        state.update(present=True, welcomed=True, left_at=None, farewelled=False)
        if self._suppressed():
            return []
        return [Effect("ROBOT_ACTION", "wave_hand", "person_entered") , Effect("SPEECH", "欢迎光临", "person_entered")]

    def _left(self, event):
        state = self._require_person(event)
        if not state["present"]:
            return []
        state["present"] = False
        state["left_at"] = event.timestamp
        if self._suppressed():
            state["farewelled"] = True
        return []

    def _tick(self, timestamp):
        if self._suppressed():
            return []
        effects = []
        for state in self._people.values():
            if (not state["present"] and state["left_at"] is not None and
                    not state["farewelled"] and timestamp - state["left_at"] >= self.absence_timeout_s):
                state["farewelled"] = True
                effects.append(Effect("SPEECH", "感谢光临，再见", "absence_timeout"))
        return effects

    def snapshot(self):
        return deepcopy({
            "absence_timeout_s": self.absence_timeout_s,
            "conversation_active": self._conversation_active,
            "meeting_active": self._meeting_active,
            "last_timestamp": self._last_timestamp,
            "people": self._people,
        })
