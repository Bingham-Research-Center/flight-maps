from __future__ import annotations

from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

from flight_maps.canonical import FlightTrack


def _bounds(lats: list[float], lons: list[float], pad: float = 0.05) -> tuple:
    lat_min, lat_max = min(lats), max(lats)
    lon_min, lon_max = min(lons), max(lons)
    dlat = (lat_max - lat_min) or 0.1
    dlon = (lon_max - lon_min) or 0.1
    return (
        lon_min - pad * dlon,
        lon_max + pad * dlon,
        lat_min - pad * dlat,
        lat_max + pad * dlat,
    )


def render(track: FlightTrack, out_path: str | Path, *, dpi: int = 300) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lats = [p.lat for p in track.positions]
    lons = [p.lon for p in track.positions]
    alts = np.array([p.alt_ft for p in track.positions])

    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent(_bounds(lats, lons), crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.LAND, facecolor="#f4f1ec")
    ax.add_feature(cfeature.OCEAN, facecolor="#dfe9f3")
    ax.add_feature(cfeature.STATES, edgecolor="#c8c8c8", linewidth=0.5)
    ax.add_feature(cfeature.RIVERS, edgecolor="#9bb8d6", linewidth=0.4)
    ax.gridlines(draw_labels=True, color="#dddddd", linewidth=0.4, alpha=0.6)

    pts = np.array([lons, lats]).T.reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc = LineCollection(
        segs,
        cmap="viridis",
        array=alts[:-1],
        linewidth=1.8,
        transform=ccrs.PlateCarree(),
    )
    ax.add_collection(lc)
    cbar = fig.colorbar(lc, ax=ax, orientation="vertical", shrink=0.7, pad=0.02)
    cbar.set_label("Altitude (ft)")

    if track.origin.get("iata"):
        ax.plot(
            track.origin["lon"],
            track.origin["lat"],
            marker="o",
            color="#222",
            markersize=6,
            transform=ccrs.PlateCarree(),
        )
        ax.text(
            track.origin["lon"] + 0.01,
            track.origin["lat"] + 0.01,
            track.origin["iata"],
            fontsize=10,
            transform=ccrs.PlateCarree(),
        )

    ax.set_title(
        f"{track.callsign} — {track.origin.get('iata','?')} → {track.destination.get('iata','?')}  "
        f"({track.depart_utc.date().isoformat() if track.depart_utc else ''})",
        fontsize=12,
    )
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return out_path
