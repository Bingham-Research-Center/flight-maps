"""Parse one flight (FR24 CSV+KML), attach screenshot metadata, and emit all viz."""
from __future__ import annotations

import argparse
from pathlib import Path

from flight_maps import metadata as md_mod
from flight_maps.parsers import fr24
from flight_maps.viz import art_topo, interactive, kepler_export, static_map

REPO = Path(__file__).resolve().parent.parent


def run(flight_id: str, *, source_dir: Path | None = None, out_dir: Path | None = None) -> None:
    source_dir = source_dir or (REPO / "test_examples/fr24")
    out_dir = out_dir or (REPO / "outputs")

    csv_path = source_dir / f"{flight_id}.csv"
    kml_path = source_dir / f"{flight_id}.kml"
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    track = fr24.parse(csv_path, kml_path if kml_path.exists() else None)
    md_mod.attach(track, REPO / "metadata")

    print(f"parsed {flight_id}: {track.callsign}, {len(track.positions)} positions")

    static_map.render(track, out_dir / f"static_{flight_id}.png")
    interactive.render(track, out_dir / f"interactive_{flight_id}.html")
    kepler_export.render(track, out_dir / f"kepler_{flight_id}")
    art_topo.render(track, out_dir / f"art_topo_{flight_id}.png")
    print(f"wrote 4 artefacts under {out_dir}/")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("flight_id", help="Stem of the CSV/KML files (e.g. 3f99ca78)")
    ap.add_argument("--source-dir", type=Path, default=None)
    ap.add_argument("--out-dir", type=Path, default=None)
    args = ap.parse_args()
    run(args.flight_id, source_dir=args.source_dir, out_dir=args.out_dir)


if __name__ == "__main__":
    main()
