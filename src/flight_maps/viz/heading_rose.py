from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from flight_maps.canonical import FlightTrack
from flight_maps.viz._watermark import stamp_example


def render(track: FlightTrack, out_path: str | Path, *, dpi: int = 220, is_example: bool = False) -> Path:
    """Polar heading 'rose' with stacked altitude bands — wind-rose styling."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    hdgs = np.array([p.heading_deg for p in track.positions], dtype=float)
    alts = np.array([p.alt_ft for p in track.positions], dtype=float)

    if alts.max() <= 0:
        bands = [(0, 1)]
    else:
        edges = np.percentile(alts[alts > 0], [0, 25, 50, 75, 100]) if (alts > 0).any() else [0, 1]
        edges = np.unique(np.round(edges))
        bands = list(zip(edges[:-1], edges[1:]))

    n_dir = 24
    bin_edges = np.linspace(0, 360, n_dir + 1)
    bin_centres = np.deg2rad((bin_edges[:-1] + bin_edges[1:]) / 2.0)
    width = 2 * np.pi / n_dir

    cmap = plt.get_cmap("viridis")
    band_colours = [cmap(i / max(1, len(bands) - 1)) for i in range(len(bands))]

    fig = plt.figure(figsize=(9, 9), facecolor="#fafaf6")
    ax = fig.add_subplot(111, projection="polar")
    ax.set_facecolor("#fafaf6")
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)

    bottom = np.zeros(n_dir)
    for (lo, hi), colour in zip(bands, band_colours):
        mask = (alts >= lo) & (alts < hi if hi != bands[-1][1] else alts <= hi)
        counts, _ = np.histogram(hdgs[mask], bins=bin_edges)
        ax.bar(
            bin_centres,
            counts,
            width=width,
            bottom=bottom,
            color=colour,
            edgecolor="#fafaf6",
            linewidth=0.6,
            label=f"{int(lo):,}–{int(hi):,} ft",
        )
        bottom += counts

    ax.set_xticks(np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315]))
    ax.set_xticklabels(["N", "NE", "E", "SE", "S", "SW", "W", "NW"], fontsize=10)
    ax.set_yticks([])
    ax.set_title(
        f"Heading rose by altitude band  ·  {track.callsign}",
        fontsize=14,
        pad=18,
    )
    ax.legend(
        title="Altitude (ft)",
        loc="lower right",
        bbox_to_anchor=(1.18, 0.0),
        fontsize=8,
        title_fontsize=9,
        frameon=False,
    )

    if is_example:
        stamp_example(fig)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_path
