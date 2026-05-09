from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal


@dataclass
class Position:
    ts: datetime
    lat: float
    lon: float
    alt_ft: int
    speed_kt: int
    heading_deg: int


@dataclass
class FlightTrack:
    flight_id: str
    track_source: Literal["fr24", "flightaware"]
    callsign: str
    origin: dict
    destination: dict
    depart_utc: datetime | None
    arrive_utc: datetime | None
    positions: list[Position]
    aircraft: dict | None = None
    weather: dict | None = None
    raw_paths: dict[str, Path | list[Path]] = field(default_factory=dict)
