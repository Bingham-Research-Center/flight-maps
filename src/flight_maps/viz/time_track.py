from __future__ import annotations

from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

from flight_maps.canonical import FlightTrack
from flight_maps.viz._watermark import stamp_example


def _bounds(lats: list[float], lons: list[float], pad: float = 0.06) -> tuple:
    lat_min, lat_max = min(lats), max(lats)
    lon_min, lon_max = min(lons), max(lons)
    dlat = (lat_max - lat_min) or 0.1
    dlon = (lon_max - lon_min) or 0.1
    return (lon_min - pad * dlon, lon_max + pad * dlon, lat_min - pad * dlat, lat_max + pad * dlat)


def render(track: FlightTrack, out_path: str | Path, *, dpi: int = 220, is_example: bool = False) -> Path:
    """Track recoloured by elapsed time, with arrow heads showing direction of travel.

    Surfaces survey ordering — which leg flew first, which last — that altitude colouring hides.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lons = np.array([p.lon for p in track.positions])
    lats = np.array([p.lat for p in track.positions])
    times = np.array([(p.ts - track.positions[0].ts).total_seconds() / 60.0 for p in track.positions])

    fig = plt.figure(figsize=(11, 9), facecolor="#0e1116")
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent(_bounds(lats.tolist(), lons.tolist()), crs=ccrs.PlateCarree())
    ax.set_facecolor("#0e1116")
    ax.add_feature(cfeature.LAND, facecolor="#181c22")
    ax.add_feature(cfeature.OCEAN, facecolor="#0a1622")
    ax.add_feature(cfeature.STATES, edgecolor="#3a4252", linewidth=0.5)
    ax.add_feature(cfeature.RIVERS, edgecolor="#2c5675", linewidth=0.4)
    gl = ax.gridlines(draw_labels=True, color="#222831", linewidth=0.4, alpha=0.6)
    gl.top_labels = False
    gl.right_labels = False

    pts = np.array([lons, lats]).T.reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc = LineCollection(
        segs,
        cmap="turbo",
        array=times[:-1],
        linewidth=2.0,
        transform=ccrs.PlateCarree(),
    )
    ax.add_collection(lc)

    # Arrow heads sampled along the track.
    n_arrows = min(20, max(5, len(lons) // 10))
    idx = np.linspace(2, len(lons) - 2, n_arrows).astype(int)
    cmap = plt.get_cmap("turbo")
    norm = plt.Normalize(times.min(), times.max())
    for i in idx:
        dx = lons[i + 1] - lons[i - 1]
        dy = lats[i + 1] - lats[i - 1]
        ax.annotate(
            "",
            xy=(lons[i] + 0.4 * dx, lats[i] + 0.4 * dy),
            xytext=(lons[i] - 0.4 * dx, lats[i] - 0.4 * dy),
            xycoords=ccrs.PlateCarree()._as_mpl_transform(ax),
            arrowprops=dict(arrowstyle="->", color=cmap(norm(times[i])), lw=1.2, alpha=0.9),
        )

    if track.origin.get("iata"):
        ax.plot(track.origin["lon"], track.origin["lat"], "o", color="#f1c40f", markersize=7, transform=ccrs.PlateCarree())
        ax.text(track.origin["lon"] + 0.005, track.origin["lat"] + 0.005, track.origin["iata"], fontsize=10, color="#f1c40f", transform=ccrs.PlateCarree())

    cbar = fig.colorbar(lc, ax=ax, pad=0.02, shrink=0.7)
    cbar.set_label("Elapsed time (min)", color="#cccccc")
    cbar.ax.yaxis.set_tick_params(color="#888888", labelsize=8)
    plt.setp(cbar.ax.get_yticklabels(), color="#cccccc")

    seg_span = float(times[:-1].max() - times[0])
    title = (
        f"{track.callsign}  ·  {track.origin.get('iata','?')} → {track.destination.get('iata','?')}"
        f"  ·  survey order  ·  legs span {seg_span:.0f} min (session {times[-1]:.0f} min)"
    )
    ax.set_title(title, color="#e0e0e0", fontsize=13, pad=12)

    if is_example:
        stamp_example(fig)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_path
