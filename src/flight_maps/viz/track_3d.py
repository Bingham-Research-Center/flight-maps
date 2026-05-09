from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from mpl_toolkits.mplot3d.art3d import Line3DCollection

from flight_maps.canonical import FlightTrack
from flight_maps.viz._watermark import stamp_example


def render(track: FlightTrack, out_path: str | Path, *, dpi: int = 220, is_example: bool = False) -> Path:
    """3D lon/lat/altitude ribbon with a ground-projection shadow."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lons = np.array([p.lon for p in track.positions])
    lats = np.array([p.lat for p in track.positions])
    alts = np.array([p.alt_ft for p in track.positions], dtype=float)
    spds = np.array([p.speed_kt for p in track.positions], dtype=float)

    fig = plt.figure(figsize=(11, 8), facecolor="#0e1116")
    ax = fig.add_subplot(111, projection="3d", facecolor="#0e1116")

    # Ground shadow (z=0) — desaturated grey trace below the airborne ribbon.
    ax.plot(lons, lats, np.zeros_like(alts), color="#3a4252", linewidth=0.7, alpha=0.7)

    # 3D ribbon coloured by speed.
    pts = np.array([lons, lats, alts]).T.reshape(-1, 1, 3)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    norm = plt.Normalize(spds.min(), spds.max() if spds.max() > spds.min() else spds.min() + 1)
    lc = Line3DCollection(segs, cmap="plasma", norm=norm, linewidth=1.6)
    lc.set_array(spds[:-1])
    ax.add_collection3d(lc)

    # Vertical "rain" lines from the airborne track to the ground every Nth sample
    # — emphasises altitude and connects ribbon to shadow.
    step = max(1, len(lons) // 60)
    for i in range(0, len(lons), step):
        ax.plot(
            [lons[i], lons[i]],
            [lats[i], lats[i]],
            [0, alts[i]],
            color=cm.plasma(norm(spds[i])),
            alpha=0.18,
            linewidth=0.5,
        )

    # Origin marker on the ground.
    if track.origin.get("iata"):
        ax.scatter(
            [track.origin["lon"]],
            [track.origin["lat"]],
            [0],
            color="#f1c40f",
            s=40,
            edgecolor="white",
            linewidth=0.6,
            zorder=10,
        )
        ax.text(
            track.origin["lon"],
            track.origin["lat"],
            0,
            "  " + track.origin["iata"],
            color="#f1c40f",
            fontsize=9,
        )

    ax.set_xlabel("Longitude", color="#cccccc", labelpad=8)
    ax.set_ylabel("Latitude", color="#cccccc", labelpad=8)
    ax.set_zlabel("Altitude (ft)", color="#cccccc", labelpad=8)
    ax.tick_params(colors="#888888", labelsize=8)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.set_pane_color((0.06, 0.07, 0.09, 1.0))
        axis._axinfo["grid"]["color"] = (0.25, 0.27, 0.31, 0.6)

    ax.view_init(elev=22, azim=-58)

    cbar = fig.colorbar(lc, ax=ax, pad=0.08, shrink=0.55)
    cbar.set_label("Ground speed (kt)", color="#cccccc")
    cbar.ax.yaxis.set_tick_params(color="#888888", labelsize=8)
    plt.setp(cbar.ax.get_yticklabels(), color="#cccccc")

    title = (
        f"{track.callsign}  ·  {track.origin.get('iata','?')} → {track.destination.get('iata','?')}  ·  "
        f"{track.depart_utc.date().isoformat() if track.depart_utc else ''}"
    )
    fig.suptitle(title + "  —  3D track + ground shadow", color="#e0e0e0", fontsize=13, y=0.94)

    if is_example:
        stamp_example(fig)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_path
