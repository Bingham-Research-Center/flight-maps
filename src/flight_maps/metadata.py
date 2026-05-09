from __future__ import annotations

import re
from pathlib import Path

import yaml

from flight_maps.canonical import FlightTrack

_FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)
_TABLE_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(.+?)\s*\|$")


def _parse_md(path: Path) -> tuple[dict, dict]:
    """Return (frontmatter_dict, table_dict). Skips header/separator rows."""
    text = path.read_text()
    m = _FRONTMATTER.match(text)
    if not m:
        return {}, {}
    front = yaml.safe_load(m.group(1)) or {}
    body = m.group(2)

    table: dict = {}
    for line in body.splitlines():
        rm = _TABLE_ROW.match(line.strip())
        if not rm:
            continue
        k, v = rm.group(1), rm.group(2)
        if k.lower() == "field" or set(k) <= {"-", " ", ":"}:
            continue
        table[k] = v
    return front, table


def load_for_flight(metadata_dir: str | Path, flight_id: str) -> dict:
    """Collect all extra-metadata-*.md entries belonging to flight_id, keyed by `kind`."""
    metadata_dir = Path(metadata_dir)
    out: dict = {}
    for md in sorted(metadata_dir.glob("extra-metadata-*.md")):
        front, table = _parse_md(md)
        if str(front.get("flight_id", "")) != flight_id:
            continue
        kind = front.get("kind", md.stem)
        out[kind] = {"_image": front.get("source_image"), **table}
    return out


def attach(track: FlightTrack, metadata_dir: str | Path) -> FlightTrack:
    bundle = load_for_flight(metadata_dir, track.flight_id)
    if "aircraft" in bundle:
        track.aircraft = bundle["aircraft"]
    if "weather" in bundle:
        track.weather = bundle["weather"]
    flight_details = bundle.get("flight_details")
    if flight_details:
        track.raw_paths.setdefault("flight_details_image", flight_details.get("_image"))
    images = [v.get("_image") for v in bundle.values() if v.get("_image")]
    if images:
        track.raw_paths["images"] = images
    return track
