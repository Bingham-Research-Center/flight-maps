from __future__ import annotations

from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from flight_maps.canonical import FlightTrack
from flight_maps.viz._watermark import HTML_BANNER


def render(track: FlightTrack, out_path: str | Path, *, is_example: bool = False) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lats = [p.lat for p in track.positions]
    lons = [p.lon for p in track.positions]
    alts = [p.alt_ft for p in track.positions]
    speeds = [p.speed_kt for p in track.positions]
    headings = [p.heading_deg for p in track.positions]
    times = [p.ts.isoformat() for p in track.positions]

    hover = [
        f"{t}<br>alt {a} ft<br>spd {s} kt<br>hdg {h}°"
        for t, a, s, h in zip(times, alts, speeds, headings)
    ]

    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.7, 0.3],
        specs=[[{"type": "mapbox"}], [{"type": "xy"}]],
        vertical_spacing=0.05,
    )

    fig.add_trace(
        go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode="lines+markers",
            marker={"size": 4, "color": alts, "colorscale": "Viridis", "showscale": True},
            line={"width": 2, "color": "#444"},
            text=hover,
            hoverinfo="text",
            name="track",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(x=times, y=alts, mode="lines", line={"color": "#1f77b4"}, name="alt (ft)"),
        row=2,
        col=1,
    )

    centre_lat = sum(lats) / len(lats)
    centre_lon = sum(lons) / len(lons)
    fig.update_layout(
        title=f"{track.callsign} — {track.origin.get('iata','?')} → {track.destination.get('iata','?')}",
        mapbox={"style": "open-street-map", "center": {"lat": centre_lat, "lon": centre_lon}, "zoom": 8},
        showlegend=False,
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
        height=900,
    )
    fig.update_yaxes(title_text="Altitude (ft)", row=2, col=1)
    fig.update_xaxes(title_text="UTC", row=2, col=1)

    fig.write_html(out_path, include_plotlyjs="cdn")
    if is_example:
        html = out_path.read_text()
        html = html.replace("<body>", f"<body>{HTML_BANNER}", 1)
        out_path.write_text(html)
    return out_path
