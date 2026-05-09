# FlightAware CSV/KML schema — STUB

We have no FlightAware CSV/KML export sample yet. Drop one in this directory when available; the column names and KML structure differ from FR24 (different `Document` metadata layout, different position column names — historically things like `Time, Latitude, Longitude, Altitude, Groundspeed, Heading`).

When a sample lands:

1. Document the columns / KML element paths in this file.
2. Implement `src/flight_maps/parsers/flightaware.py::parse` against it (currently `NotImplementedError`).
3. Add a unit test mirroring `tests/test_parsers.py::test_fr24_parses_example`.

Note: FlightAware **iOS app** screenshots are a different artefact entirely — those feed `metadata/extra-metadata-*.md`, not this parser.
