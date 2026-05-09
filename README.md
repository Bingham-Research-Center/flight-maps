# flight-maps

Visualise FlightRadar24 (FR24) CSV+KML flight tracks alongside metadata from the FlightAware iOS app, producing static publication maps, interactive web views, Kepler.gl 3D ribbons, and minimalist topographic line-art.

Built at the Bingham Research Center, Utah State University, for the Uinta Basin research-flight programme.

## Data sources

- **CSV / KML track exports**: FlightRadar24. Schema: `test_examples/fr24/SCHEMA.md`.
- **App screenshots → metadata**: FlightAware iOS app. Transcribed into `metadata/extra-metadata-<image>.md`.

A future FlightAware CSV/KML exporter is supported by stub at `src/flight_maps/parsers/flightaware.py`; populate when a sample arrives.

## Quickstart

```bash
mamba env create -f environment.yml
mamba activate flight-maps
pip install -e .

pytest -q
python scripts/run_all.py 3f99ca78
```

Outputs land in `outputs/`:

- `static_3f99ca78.png` — cartopy publication map.
- `interactive_3f99ca78.html` — Plotly map + altitude profile.
- `kepler_3f99ca78/{track.csv,config.json}` — drag into <https://kepler.gl/demo>.
- `art_topo_3f99ca78.png` — minimalist topographic line-art.

## Adding a new flight

1. Drop FR24 `<id>.csv` and `<id>.kml` into `test_examples/fr24/` (or any directory; pass full paths).
2. Add screenshots to `images/` and transcribe each into `metadata/extra-metadata-<image-stem>.md` using `metadata/TEMPLATE.md`.
3. Create `metadata/flight-<id>.md` linking the per-image files.
4. `python scripts/run_all.py <id>`.

## Repo map

See [CLAUDE.md](CLAUDE.md) for the indexed cold-start view used by AI agents (and humans in a hurry).

## License

MIT — see [LICENSE](LICENSE).
