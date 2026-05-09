from __future__ import annotations

from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
from cartopy.io.shapereader import natural_earth, Reader
from matplotlib.font_manager import FontProperties

from flight_maps.canonical import FlightTrack
from flight_maps.viz._watermark import stamp_example


def _bounds(lats: list[float], lons: list[float], pad: float = 0.12) -> tuple:
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


def render(track: FlightTrack, out_path: str | Path, *, dpi: int = 300, is_example: bool = False) -> Path:
    """Minimalist topographic line-art: greyscale relief + thin accent track + sparse label."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lats = [p.lat for p in track.positions]
    lons = [p.lon for p in track.positions]

    fig = plt.figure(figsize=(7, 9), facecolor="#fafaf6")
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent(_bounds(lats, lons), crs=ccrs.PlateCarree())
    ax.set_facecolor("#fafaf6")

    ax.add_feature(cfeature.LAND, facecolor="#f1ede4", edgecolor="none")
    ax.add_feature(cfeature.OCEAN, facecolor="#e6ece6")

    try:
        roads_path = natural_earth(resolution="10m", category="cultural", name="roads")
        ax.add_geometries(
            list(Reader(roads_path).geometries()),
            ccrs.PlateCarree(),
            edgecolor="#bdb6a8",
            facecolor="none",
            linewidth=0.3,
        )
    except Exception:
        pass

    ax.add_feature(cfeature.RIVERS, edgecolor="#c8d2c0", linewidth=0.3)
    ax.add_feature(cfeature.LAKES, facecolor="#dde6db", edgecolor="none")
    ax.add_feature(cfeature.STATES, edgecolor="#d8d3c4", linewidth=0.4, linestyle=":")

    ax.plot(
        lons,
        lats,
        color="#c0392b",
        linewidth=1.0,
        solid_capstyle="round",
        transform=ccrs.PlateCarree(),
    )

    serif = FontProperties(family="serif", size=9)
    if track.origin.get("iata"):
        ax.plot(
            track.origin["lon"],
            track.origin["lat"],
            marker="o",
            color="#222",
            markersize=3,
            transform=ccrs.PlateCarree(),
        )
        ax.text(
            track.origin["lon"] + 0.015,
            track.origin["lat"],
            track.origin["iata"],
            fontproperties=serif,
            transform=ccrs.PlateCarree(),
        )

    ax.set_title(track.callsign, fontproperties=FontProperties(family="serif", size=14), pad=14)

    for spine in ax.spines.values():
        spine.set_visible(False)

    if is_example:
        stamp_example(fig)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_path
