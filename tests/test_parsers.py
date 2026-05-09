from pathlib import Path

import pytest

from flight_maps.parsers import flightaware, fr24

EXAMPLE = Path(__file__).resolve().parent.parent / "test_examples/fr24"


def test_fr24_parses_example():
    track = fr24.parse(EXAMPLE / "3f99ca78.csv", EXAMPLE / "3f99ca78.kml")
    assert track.callsign == "N91MG"
    assert track.track_source == "fr24"
    assert track.flight_id == "3f99ca78"
    assert len(track.positions) > 50
    p = track.positions[0]
    assert -180 <= p.lon <= 180
    assert -90 <= p.lat <= 90
    assert track.origin["iata"] == "VEL"
    assert track.destination["iata"] == "VEL"


def test_flightaware_stub_raises():
    with pytest.raises(NotImplementedError):
        flightaware.parse("dummy.csv")
