from __future__ import annotations

from matplotlib.figure import Figure


def stamp_example(fig: Figure, *, label: str = "EXAMPLE OUTPUT") -> None:
    """Overlay a large diagonal 'EXAMPLE OUTPUT' watermark across the figure.

    Used to mark committed reference renders so they cannot be mistaken
    for production research output.
    """
    fig.text(
        0.5,
        0.5,
        label,
        fontsize=72,
        color="#c0392b",
        alpha=0.18,
        ha="center",
        va="center",
        rotation=30,
        weight="bold",
        zorder=10,
    )
    fig.text(
        0.99,
        0.01,
        "example / scaffolding render — not for analysis",
        fontsize=8,
        color="#777",
        ha="right",
        va="bottom",
        style="italic",
        zorder=10,
    )


HTML_BANNER = (
    '<div style="background:#fff3cd;border-bottom:2px solid #c0392b;'
    "color:#7d2a1d;font-family:system-ui,sans-serif;font-size:14px;"
    'padding:10px 16px;text-align:center;font-weight:600;">'
    "EXAMPLE OUTPUT — scaffolding render of the bundled demo flight, "
    "not for analysis.</div>"
)
