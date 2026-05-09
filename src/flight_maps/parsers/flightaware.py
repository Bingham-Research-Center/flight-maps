from __future__ import annotations

from pathlib import Path

from flight_maps.canonical import FlightTrack


def parse(csv_path: str | Path, kml_path: str | Path | None = None) -> FlightTrack:
    raise NotImplementedError(
        "FlightAware CSV/KML parser stub. Populate test_examples/flightaware/ "
        "with a sample export and implement against that schema "
        "(differs from FR24 — see test_examples/flightaware/SCHEMA.md)."
    )
