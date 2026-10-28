from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Event:
    """Подія, прочитана з журналу."""
    ts: str
    kind: str
    fields: dict = field(default_factory=dict)


def load_events(path):
    """Завантажує коректні події з журналу."""
    events = []

    with open(path, encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            parts = line.split("|")

            if len(parts) < 2:
                continue

            ts, kind, *pairs = parts

            # Перевіряємо формат і реальність дати та часу.
            try:
                datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                continue

            if not kind or not pairs:
                continue

            # Рядок має містити коректні пари ключ=значення.
            fields = {}

            try:
                for pair in pairs:
                    key, value = pair.split("=", 1)

                    if not key:
                        raise ValueError

                    fields[key] = value

            except ValueError:
                continue

            events.append(Event(ts, kind, fields))

    return events


def events_between(events, start, end):
    """Повертає події в інтервалі [start, end)."""
    start_dt = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
    end_dt = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")

    if start_dt > end_dt:
        raise ValueError("Початок інтервалу пізніший за кінець")

    result = []

    for event in events:
        event_dt = datetime.strptime(
            event.ts, "%Y-%m-%dT%H:%M:%S"
        )

        if start_dt <= event_dt < end_dt:
            result.append(event)

    return result


def gate_openings(events, gate, start, end):
    """Повертає відкриття конкретних воріт за заданий час."""
    return [
        event
        for event in events_between(events, start, end)
        if event.kind == "GATE"
        and event.fields.get("gate") == str(gate)
        and event.fields.get("action") == "open"
    ]


def zone_access(events, zone, start, end):
    """Повертає події доступу до конкретної зони."""
    return [
        event
        for event in events_between(events, start, end)
        if event.kind == "ACCESS"
        and event.fields.get("zone") == zone
    ]


def sensor_alerts(events, zone, sensor_type, start, end):
    """Повертає показники датчика конкретного типу в зоні."""
    return [
        event
        for event in events_between(events, start, end)
        if event.kind == "SENSOR"
        and event.fields.get("zone") == zone
        and event.fields.get("type") == sensor_type
    ]


def batch_movements(events, batch):
    """Повертає всі переміщення конкретної партії."""
    return [
        event
        for event in events
        if event.kind == "CARGO"
        and event.fields.get("batch") == batch
    ]


def alarm_enabled_at(events, moment):
    """Перевіряє, чи була ввімкнена загальна сигналізація."""
    moment_dt = datetime.strptime(moment, "%Y-%m-%dT%H:%M:%S")
    enabled = True

    for event in sorted(events, key=lambda item: item.ts):
        event_dt = datetime.strptime(
            event.ts, "%Y-%m-%dT%H:%M:%S"
        )

        if event_dt > moment_dt:
            break

        if (
            event.kind == "ALARM"
            and event.fields.get("zone") == "all"
        ):
            enabled = event.fields.get("action") != "disable"

    return enabled
