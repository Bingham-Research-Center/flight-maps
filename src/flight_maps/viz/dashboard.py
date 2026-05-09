from __future__ import annotations

from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.gridspec import GridSpec

from flight_maps.canonical import FlightTrack
from flight_maps.viz._watermark import stamp_example


def _bounds(lats: list[float], lons: list[float], pad: float = 0.08) -> tuple:
    lat_min, lat_max = min(lats), max(lats)
    lon_min, lon_max = min(lons), max(lons)
    dlat = (lat_max - lat_min) or 0.1
    dlon = (lon_max - lon_min) or 0.1
    return (lon_min - pad * dlon, lon_max + pad * dlon, lat_min - pad * dlat, lat_max + pad * dlat)


def render(track: FlightTrack, out_path: str | Path, *, dpi: int = 220, is_example: bool = False) -> Path:
    """Composite 'telemetry dashboard' PNG: track + altitude/speed time-series + heading rose."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lons = np.array([p.lon for p in track.positions])
    lats = np.array([p.lat for p in track.positions])
    alts = np.array([p.alt_ft for p in track.positions], dtype=float)
    spds = np.array([p.speed_kt for p in track.positions], dtype=float)
    hdgs = np.array([p.heading_deg for p in track.positions], dtype=float)
    times = np.array([p.ts for p in track.positions])
    elapsed_min = np.array([(t - times[0]).total_seconds() / 60.0 for t in times])

    fig = plt.figure(figsize=(15, 10), facecolor="#fafaf6")
    gs = GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.32, left=0.05, right=0.97, top=0.93, bottom=0.07)

    # Track map (large left block).
    ax_map = fig.add_subplot(gs[:, :2], projection=ccrs.PlateCarree())
    ax_map.set_extent(_bounds(lats.tolist(), lons.tolist()), crs=ccrs.PlateCarree())
    ax_map.add_feature(cfeature.LAND, facecolor="#f1ede4")
    ax_map.add_feature(cfeature.OCEAN, facecolor="#dfe9f3")
    ax_map.add_feature(cfeature.STATES, edgecolor="#c8c8c8", linewidth=0.5)
    ax_map.add_feature(cfeature.RIVERS, edgecolor="#9bb8d6", linewidth=0.4)
    ax_map.gridlines(draw_labels=True, color="#dddddd", linewidth=0.4, alpha=0.6)

    pts = np.array([lons, lats]).T.reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc = LineCollection(segs, cmap="viridis", array=alts[:-1], linewidth=1.6, transform=ccrs.PlateCarree())
    ax_map.add_collection(lc)
    cbar = fig.colorbar(lc, ax=ax_map, orientation="horizontal", pad=0.04, shrink=0.7)
    cbar.set_label("Altitude (ft)")

    if track.origin.get("iata"):
        ax_map.plot(track.origin["lon"], track.origin["lat"], "o", color="#222", markersize=6, transform=ccrs.PlateCarree())
        ax_map.text(track.origin["lon"] + 0.005, track.origin["lat"] + 0.005, track.origin["iata"], fontsize=9, transform=ccrs.PlateCarree())

    ax_map.set_title("Track (colour = altitude)", fontsize=11, loc="left")

    # Altitude vs time.
    ax_alt = fig.add_subplot(gs[0, 2])
    ax_alt.plot(elapsed_min, alts, color="#2c7fb8", linewidth=1.2)
    ax_alt.fill_between(elapsed_min, alts, color="#2c7fb8", alpha=0.18)
    ax_alt.set_title("Altitude vs time", fontsize=10, loc="left")
    ax_alt.set_xlabel("min", fontsize=8)
    ax_alt.set_ylabel("ft", fontsize=8)
    ax_alt.tick_params(labelsize=8)
    ax_alt.grid(True, alpha=0.3)

    # Speed vs time.
    ax_spd = fig.add_subplot(gs[1, 2])
    ax_spd.plot(elapsed_min, spds, color="#d95f0e", linewidth=1.2)
    ax_spd.fill_between(elapsed_min, spds, color="#d95f0e", alpha=0.15)
    ax_spd.set_title("Ground speed vs time", fontsize=10, loc="left")
    ax_spd.set_xlabel("min", fontsize=8)
    ax_spd.set_ylabel("kt", fontsize=8)
    ax_spd.tick_params(labelsize=8)
    ax_spd.grid(True, alpha=0.3)

    # Heading rose (compact polar histogram).
    ax_rose = fig.add_subplot(gs[2, 2], projection="polar")
    bins = np.linspace(0, 2 * np.pi, 33)
    counts, _ = np.histogram(np.deg2rad(hdgs), bins=bins)
    widths = np.diff(bins)
    ax_rose.bar(bins[:-1], counts, width=widths, bottom=0, color="#7f3b08", edgecolor="#fafaf6", alpha=0.85)
    ax_rose.set_theta_zero_location("N")
    ax_rose.set_theta_direction(-1)
    ax_rose.set_xticks(np.deg2rad([0, 90, 180, 270]))
    ax_rose.set_xticklabels(["N", "E", "S", "W"], fontsize=8)
    ax_rose.set_yticks([])
    ax_rose.set_title("Heading distribution", fontsize=10, loc="left", pad=10)

    # Header text using metadata if attached.
    aircraft = track.aircraft or {}
    sub = []
    if aircraft.get("Make") or aircraft.get("Model"):
        sub.append(f"{aircraft.get('Year','')} {aircraft.get('Make','')} {aircraft.get('Model','')}".strip())
    if track.depart_utc:
        sub.append(track.depart_utc.strftime("%Y-%m-%d %H:%M UTC"))
    if track.weather:
        wx = track.weather
        if wx.get("Takeoff Wind"):
            sub.append(f"wind {wx['Takeoff Wind']}")
        if wx.get("Takeoff Temperature"):
            sub.append(f"temp {wx['Takeoff Temperature']}")

    title = (
        f"{track.callsign}  ·  {track.origin.get('iata','?')} → {track.destination.get('iata','?')}  ·  "
        f"{len(track.positions)} samples over {elapsed_min[-1]:.0f} min"
    )
    fig.suptitle(title, fontsize=14, y=0.985, ha="center")
    if sub:
        fig.text(0.5, 0.955, "  ·  ".join(sub), ha="center", fontsize=9, color="#666")

    if is_example:
        stamp_example(fig)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_path
