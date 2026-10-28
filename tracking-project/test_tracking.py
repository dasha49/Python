from datetime import datetime, timedelta
from pathlib import Path

import pytest

from tracking import (
    Event,
    load_events,
    events_between,
    gate_openings,
    zone_access,
    sensor_alerts,
    batch_movements,
    alarm_enabled_at,
)


@pytest.fixture(scope="session")
def events():
    """Завантажує журнал один раз для всіх тестів."""
    log_path = Path(__file__).with_name("hub_log.txt")
    return load_events(log_path)



def test_dispatcher_statement(events):
    """Перевіряє свідчення диспетчера про партію 4-А."""

    start = "2026-10-13T22:10:00"
    end = "2026-10-13T22:11:00"

    # Перевіряємо, чи відкрили ворота 1 о 22:10.
    gates = gate_openings(events, 1, start, end)

    assert any(
        event.ts == "2026-10-13T22:10:04"
        for event in gates
    ), "Ворота 1 не були відкриті о 22:10"

    # Знаходимо відвантаження через ворота 1,
    # не покладаючись на пошкоджену назву партії.
    shipments = [
        event
        for event in events
        if event.kind == "CARGO"
        and event.fields.get("gate") == "1"
        and event.fields.get("action") == "out"
        and event.ts.startswith("2026-10-13T22:")
    ]

    shipment = next(
        (
            event for event in shipments
            if event.ts == "2026-10-13T22:11:02"
        ),
        None,
    )

    assert shipment is not None, (
        "Не знайдено відвантаження через ворота 1 о 22:11:02"
    )

   # Журнал підтверджує відкриття воріт о 22:10,
    # але відвантаження зафіксовано о 22:11:02.
    assert shipment.ts == "2026-10-13T22:11:02"
    assert shipment.fields.get("gate") == "1"
    assert shipment.fields.get("action") == "out"



def test_guard_statement(events):
    """Перевіряє свідчення охоронця про сектор C."""
    start = "2026-10-13T23:00:00"
    end = "2026-10-14T03:00:00"

    accesses = zone_access(events, "C", start, end)

    assert any(
        event.ts == "2026-10-14T00:41:30"
        and event.fields.get("card") == "BLUE-0417"
        for event in accesses
    )


def test_engineer_statement(events):
    """Перевіряє спрацювання датчика диму."""
    start = "2026-10-14T02:47:00"
    end = "2026-10-14T02:48:00"

    alerts = sensor_alerts(
        events, "C", "smoke", start, end
    )

    assert any(
        event.ts == "2026-10-14T02:47:55"
        for event in alerts
    )


def test_events_between_crosses_midnight():
    """Перевіряє правильність інтервалу через північ."""
    events = [
        Event("2026-10-13T23:59:00", "TEST"),
        Event("2026-10-14T00:00:00", "TEST"),
        Event("2026-10-14T00:01:00", "TEST"),
    ]

    result = events_between(
        events,
        "2026-10-13T23:59:00",
        "2026-10-14T00:01:00",
    )

    assert [event.ts for event in result] == [
        "2026-10-13T23:59:00",
        "2026-10-14T00:00:00",
    ]


def test_load_events_skips_corrupted_lines(tmp_path):
    """Перевіряє, що пошкоджені рядки не ламають завантаження."""
    log_path = tmp_path / "test_log.txt"

    log_path.write_text(
        "2026-10-14T00:00:00|SYSTEM|status=ok\n"
        "&??^{(<&>~%<*@]^$\n"
        "2026-13-40T25:61:00|GATE|gate=1|action=open\n"
        "2026-10-14T00:01:00|SENSOR|zone=C|type=smoke\n"
        "2026-10-14T00:02:00|SYSTEM\n",
        encoding="utf-8",
    )

    result = load_events(log_path)

    assert len(result) == 2
    assert result[0].kind == "SYSTEM"
    assert result[1].kind == "SENSOR"


def test_alarm_was_disabled_before_fire(events):
    """Перевіряє стан сигналізації в момент спрацювання датчика."""
    fire_time = "2026-10-14T02:47:55"

    assert alarm_enabled_at(events, fire_time) is False


def test_alarm_disable_event_exists(events):
    """Перевіряє запис про вимкнення сигналізації."""
    disable_events = [
        event for event in events
        if event.kind == "ALARM"
        and event.fields.get("zone") == "all"
        and event.fields.get("action") == "disable"
    ]

    assert any(
        event.ts == "2026-10-14T00:35:12"
        for event in disable_events
    )
