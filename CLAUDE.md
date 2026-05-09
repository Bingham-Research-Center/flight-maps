# CLAUDE.md — flight-maps cold-start index

Visualise FlightRadar24 (FR24) CSV+KML flight tracks plus FlightAware iOS app metadata; emit static, interactive, Kepler.gl, and minimalist topographic-art maps. Single-flight scaffold; multi-flight pattern is the obvious extension.

## Activate

```bash
mamba activate flight-maps        # or: mamba env create -f environment.yml
pip install -e .                  # first run only
```

## Provenance (do not invert)

- **CSV / KML** in `test_examples/fr24/` are FR24 exports.
- **JPG screenshots** in `images/` are FlightAware iOS app captures, transcribed into `metadata/extra-metadata-*.md`.

## File map

| Concern | Path |
|---|---|
| Canonical record (`FlightTrack`, `Position`) | `src/flight_maps/canonical.py` |
| FR24 parser (CSV+KML → FlightTrack) | `src/flight_maps/parsers/fr24.py` |
| FlightAware parser (stub) | `src/flight_maps/parsers/flightaware.py` |
| Metadata loader (md → dict, attaches to track) | `src/flight_maps/metadata.py` |
| Static cartopy map | `src/flight_maps/viz/static_map.py` |
| Plotly interactive HTML | `src/flight_maps/viz/interactive.py` |
| Kepler.gl export (CSV+config) | `src/flight_maps/viz/kepler_export.py` |
| Topographic line-art | `src/flight_maps/viz/art_topo.py` |
| 3D track + ground shadow | `src/flight_maps/viz/track_3d.py` |
| Telemetry dashboard composite | `src/flight_maps/viz/dashboard.py` |
| Heading rose (altitude-banded) | `src/flight_maps/viz/heading_rose.py` |
| Time-coloured 2D track | `src/flight_maps/viz/time_track.py` |
| Watermark helper | `src/flight_maps/viz/_watermark.py` |
| End-to-end runner | `scripts/run_all.py` |
| Tests | `tests/test_parsers.py` |
| FR24 schema doc | `test_examples/fr24/SCHEMA.md` |
| FA schema stub | `test_examples/flightaware/SCHEMA.md` |
| Metadata template | `metadata/TEMPLATE.md` |

## Canonical record (only schema inlined)

| field | type | notes |
|---|---|---|
| flight_id | str | filename stem |
| track_source | "fr24" \| "flightaware" | which exporter for CSV/KML |
| callsign | str | tail / callsign |
| origin / destination | dict | `{icao, iata, name, city, lat, lon}` |
| depart_utc / arrive_utc | datetime\|None | from KML or first/last sample |
| positions | list[Position] | `(ts, lat, lon, alt_ft, speed_kt, heading_deg)` |
| aircraft | dict\|None | from `metadata/extra-metadata-*.md` (kind=aircraft) |
| weather | dict\|None | from `metadata/extra-metadata-*.md` (kind=weather) |
| raw_paths | dict | `{csv, kml, images: [...]}` |

## Per-flight metadata index (paths only — load on demand)

| flight_id | record |
|---|---|
| 3f99ca78 | `metadata/flight-3f99ca78.md` (links 3 per-image files) |

## Common tasks

- Run all viz (analysis): `python scripts/run_all.py 3f99ca78`
- Run all viz (committed reference): `python scripts/run_all.py 3f99ca78 --example --out-dir examples/3f99ca78`
- Tests: `pytest -q`
- New flight: drop `<id>.{csv,kml}` into `test_examples/fr24/`, transcribe screenshots into `metadata/extra-metadata-<image-stem>.md`, add `metadata/flight-<id>.md`, then `python scripts/run_all.py <id>`.
- Implement FlightAware parser: see `test_examples/flightaware/SCHEMA.md`.

## Outputs

- `outputs/` (gitignored): scratch dir for analysis runs.
- `examples/3f99ca78/` (committed): reference renders of the demo flight, watermarked `EXAMPLE OUTPUT` via `--example`. Used in README. Regenerate with the `--example` invocation above.
- Per output: `static_<id>.png`, `art_topo_<id>.png`, `track_3d_<id>.png`, `dashboard_<id>.png`, `heading_rose_<id>.png`, `time_track_<id>.png`, `interactive_<id>.html`, `kepler_<id>/{track.csv,config.json,README.md}`.
