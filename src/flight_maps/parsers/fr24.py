from __future__ import annotations

import csv
import re
from datetime import datetime, timezone
from pathlib import Path

from lxml import etree

from flight_maps.canonical import FlightTrack, Position

_KML_NS = {"kml": "http://www.opengis.net/kml/2.2"}


def _parse_position_field(raw: str) -> tuple[float, float]:
    lat_s, lon_s = raw.split(",")
    return float(lat_s), float(lon_s)


def _read_csv(path: Path) -> tuple[str, list[Position]]:
    callsign = ""
    positions: list[Position] = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            callsign = row["Callsign"]
            lat, lon = _parse_position_field(row["Position"].strip('"'))
            positions.append(
                Position(
                    ts=datetime.fromisoformat(row["UTC"].replace("Z", "+00:00")),
                    lat=lat,
                    lon=lon,
                    alt_ft=int(row["Altitude"]),
                    speed_kt=int(row["Speed"]),
                    heading_deg=int(row["Direction"]),
                )
            )
    return callsign, positions


def _read_kml_metadata(path: Path) -> dict:
    """Pull origin/destination/ATD/ETA from the document-level <description> CDATA.

    FR24 embeds these as styled HTML; we regex what we need rather than render.
    """
    tree = etree.parse(str(path))
    desc_el = tree.find("kml:Document/kml:description", _KML_NS)
    desc = desc_el.text if desc_el is not None and desc_el.text else ""

    # Two <h3>CODE</h3> blocks — origin then destination — followed by city in plain text.
    airport_codes = re.findall(r"<h3[^>]*>([A-Z]{3,4})</h3>([A-Za-z\s]+)</a>", desc)
    origin_code, origin_city = (airport_codes[0] if airport_codes else ("", ""))
    dest_code, dest_city = (
        airport_codes[1] if len(airport_codes) >= 2 else (origin_code, origin_city)
    )

    atd = re.search(r'title="Actual Time of Departure".*?title="([^"]+)"', desc, re.S)
    eta = re.search(r'title="Estimated Time of Arrival".*?title="([^"]+)"', desc, re.S)

    def _to_utc(s: str | None) -> datetime | None:
        if not s:
            return None
        try:
            return datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        except ValueError:
            return None

    return {
        "origin_code": origin_code,
        "origin_city": origin_city.strip(),
        "destination_code": dest_code,
        "destination_city": dest_city.strip(),
        "depart_utc": _to_utc(atd.group(1) if atd else None),
        "arrive_utc": _to_utc(eta.group(1) if eta else None),
    }


def parse(csv_path: str | Path, kml_path: str | Path | None = None) -> FlightTrack:
    """Parse an FR24 CSV (and optional matching KML) into a FlightTrack."""
    csv_path = Path(csv_path)
    flight_id = csv_path.stem

    callsign, positions = _read_csv(csv_path)

    meta = {}
    if kml_path is not None:
        kml_path = Path(kml_path)
        meta = _read_kml_metadata(kml_path)

    first = positions[0] if positions else None
    last = positions[-1] if positions else None

    origin = {
        "icao": ("K" + meta.get("origin_code", "")) if meta.get("origin_code") else "",
        "iata": meta.get("origin_code", ""),
        "name": f"{meta.get('origin_city','')} Airport".strip(),
        "city": meta.get("origin_city", ""),
        "lat": first.lat if first else None,
        "lon": first.lon if first else None,
    }
    destination = {
        "icao": (
            ("K" + meta.get("destination_code", ""))
            if meta.get("destination_code")
            else ""
        ),
        "iata": meta.get("destination_code", ""),
        "name": f"{meta.get('destination_city','')} Airport".strip(),
        "city": meta.get("destination_city", ""),
        "lat": last.lat if last else None,
        "lon": last.lon if last else None,
    }

    return FlightTrack(
        flight_id=flight_id,
        track_source="fr24",
        callsign=callsign,
        origin=origin,
        destination=destination,
        depart_utc=meta.get("depart_utc") or (first.ts if first else None),
        arrive_utc=meta.get("arrive_utc") or (last.ts if last else None),
        positions=positions,
        raw_paths={"csv": csv_path, "kml": kml_path} if kml_path else {"csv": csv_path},
    )
