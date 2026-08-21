import pytest

from robot_application import Event, RobotApplication


def event(kind, timestamp, person_id="p1"):
    return Event(kind, timestamp, person_id)


def values(effects):
    return [effect.value for effect in effects]


def test_first_welcome_and_repeated_entry():
    app = RobotApplication()
    assert values(app.handle_event(event("PERSON_ENTERED", 0))) == ["wave_hand", "欢迎光临"]
    assert app.handle_event(event("PERSON_ENTERED", 1)) == []


@pytest.mark.parametrize("prefix", ["CONVERSATION", "MEETING"])
def test_interaction_suppresses_welcome_without_replay(prefix):
    app = RobotApplication()
    app.handle_event(event(f"{prefix}_STARTED", 0, None))
    assert app.handle_event(event("PERSON_ENTERED", 1)) == []
    assert app.handle_event(event(f"{prefix}_ENDED", 2, None)) == []
    assert app.handle_event(event("PERSON_ENTERED", 3)) == []


def test_departure_during_interaction_is_not_replayed():
    app = RobotApplication()
    app.handle_event(event("PERSON_ENTERED", 0))
    app.handle_event(event("MEETING_STARTED", 1, None))
    app.handle_event(event("PERSON_LEFT", 2))
    app.handle_event(event("MEETING_ENDED", 3, None))
    assert app.handle_event(event("TICK", 12, None)) == []


def test_farewell_after_ten_seconds_and_only_once():
    app = RobotApplication()
    app.handle_event(event("PERSON_ENTERED", 0))
    app.handle_event(event("PERSON_LEFT", 5))
    assert app.handle_event(event("TICK", 14, None)) == []
    assert values(app.handle_event(event("TICK", 15, None))) == ["感谢光临，再见"]
    assert app.handle_event(event("TICK", 16, None)) == []


def test_short_absence_return_has_no_farewell_or_new_welcome():
    app = RobotApplication()
    app.handle_event(event("PERSON_ENTERED", 0))
    app.handle_event(event("PERSON_LEFT", 2))
    assert app.handle_event(event("PERSON_ENTERED", 5)) == []
    assert app.handle_event(event("TICK", 20, None)) == []


def test_completed_departure_starts_new_reception():
    app = RobotApplication()
    app.handle_event(event("PERSON_ENTERED", 0))
    app.handle_event(event("PERSON_LEFT", 1))
    app.handle_event(event("TICK", 11, None))
    assert values(app.handle_event(event("PERSON_ENTERED", 20))) == ["wave_hand", "欢迎光临"]


def test_people_have_independent_lifecycles():
    app = RobotApplication()
    assert len(app.handle_event(event("PERSON_ENTERED", 0, "p1"))) == 2
    assert len(app.handle_event(event("PERSON_ENTERED", 1, "p2"))) == 2
    app.handle_event(event("PERSON_LEFT", 2, "p1"))
    assert len(app.handle_event(event("TICK", 12, None))) == 1
    assert app.snapshot()["people"]["p2"]["present"] is True


def test_snapshot_is_detached():
    app = RobotApplication()
    app.handle_event(event("PERSON_ENTERED", 0))
    snapshot = app.snapshot()
    snapshot["people"]["p1"]["present"] = False
    assert app.snapshot()["people"]["p1"]["present"] is True


def test_invalid_event_and_stale_timestamp_are_rejected():
    app = RobotApplication()
    with pytest.raises(ValueError):
        app.handle_event(event("PERSON_ENTERED", 0, None))
    with pytest.raises(ValueError):
        app.handle_event(event("UNKNOWN", 1, None))
    with pytest.raises(ValueError):
        app.handle_event(event("TICK", 0, None))


def test_negative_timeout_is_rejected():
    with pytest.raises(ValueError):
        RobotApplication(-1)
