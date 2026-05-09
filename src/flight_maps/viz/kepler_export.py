from __future__ import annotations

import csv
import json
from pathlib import Path

from flight_maps.canonical import FlightTrack


def render(track: FlightTrack, out_dir: str | Path) -> Path:
    """Emit track.csv + config.json for kepler.gl/demo (drag both onto the page)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / "track.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "lat", "lon", "alt_ft", "speed_kt", "heading_deg"])
        for p in track.positions:
            w.writerow([p.ts.isoformat(), p.lat, p.lon, p.alt_ft, p.speed_kt, p.heading_deg])

    centre_lat = sum(p.lat for p in track.positions) / len(track.positions)
    centre_lon = sum(p.lon for p in track.positions) / len(track.positions)

    config = {
        "version": "v1",
        "config": {
            "visState": {
                "layers": [
                    {
                        "id": "track",
                        "type": "trip",
                        "config": {
                            "dataId": "track",
                            "label": f"{track.callsign} track",
                            "color": [255, 153, 31],
                            "columns": {
                                "lat": "lat",
                                "lng": "lon",
                                "altitude": "alt_ft",
                                "timestamp": "timestamp",
                            },
                            "isVisible": True,
                            "visConfig": {"thickness": 1.5, "sizeRange": [0, 10]},
                        },
                    }
                ]
            },
            "mapState": {"latitude": centre_lat, "longitude": centre_lon, "zoom": 9, "pitch": 45},
            "mapStyle": {"styleType": "dark"},
        },
    }
    cfg_path = out_dir / "config.json"
    cfg_path.write_text(json.dumps(config, indent=2))

    readme = out_dir / "README.md"
    readme.write_text(
        "# Kepler.gl export\n\n"
        "1. Open <https://kepler.gl/demo>.\n"
        "2. Drag `track.csv` onto the map.\n"
        "3. Open the menu → Load map config → drag `config.json`.\n"
    )
    return out_dir
