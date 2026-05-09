# FlightRadar24 (FR24) export schema

Two paired files per flight, sharing a stem (e.g. `3f99ca78`):

## CSV (`<id>.csv`) — track samples

| Column | Type | Notes |
|---|---|---|
| Timestamp | int | Unix seconds (UTC) |
| UTC | str | ISO 8601 with `Z` suffix |
| Callsign | str | Aircraft callsign / tail (e.g. `N91MG`) |
| Position | str | `"lat,lon"` quoted as a single CSV field |
| Altitude | int | Feet above MSL |
| Speed | int | Knots ground speed |
| Direction | int | Heading in degrees (0–359) |

Header row is present; one row per sample (typically a few seconds apart). Position is comma-separated *inside the quoted field* — split on `,` after stripping quotes.

## KML (`<id>.kml`) — visual route + flight metadata

- Root: `<kml><Document>`. Document `<name>` is `-/<Callsign>`.
- Document `<description>` is HTML inside CDATA, embedding:
  - Origin & destination airport codes (each as `<h3>CODE</h3>City`).
  - `Actual Time of Departure` and `Estimated Time of Arrival` as `title` attributes on inner `<span>`s, e.g. `title="2026-05-08 17:04"`.
  - Aircraft type (`<span>` after “Aircraft” label) and registration.
- Single `<Folder><name>Route</name>` containing one `<Placemark>` per sample:
  - `<name>` — human ISO timestamp.
  - `<description>` — HTML CDATA with `Altitude / Speed / Heading`.
  - `<TimeStamp><when>YYYY-MM-DDTHH:MM:SS+00:00</when></TimeStamp>`.
  - `<Style><IconStyle><heading>...</heading><Icon><href>…airports.png</href></Icon></IconStyle></Style>`.
  - `<Point><altitudeMode>absolute</altitudeMode><coordinates>lon,lat,alt_m</coordinates></Point>`.

## Parser

`src/flight_maps/parsers/fr24.py::parse(csv_path, kml_path)` returns a `FlightTrack`. CSV is the authoritative position source; the KML is queried for origin/destination + ATD/ETA only (regex over the description CDATA).

## Example

`3f99ca78.csv` and `3f99ca78.kml` in this directory: a research flight from KVEL out and back over the Uinta Basin, 2026-05-08, ~63 minutes airborne.
