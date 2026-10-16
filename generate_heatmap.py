"""Render the GitHub contribution calendar as caldera-themed SVGs (dark + light).

Data comes from the public API at github-contributions-api.jogruber.de, so no
token is needed. Run: python generate_heatmap.py <username>
"""
import json
import sys
import urllib.request
from datetime import date

USER = sys.argv[1] if len(sys.argv) > 1 else "santinovargasdb"

CELL, GAP, RX = 13, 3, 3
LEFT, TOP, PAD = 34, 30, 14
THEMES = {
    "dark": dict(bg="#1a1612", border="#e84e1b", label="#7a6f60",
                 levels=["#2b241e", "#6b2a10", "#a83a12", "#e84e1b", "#ff7a3d"]),
    "light": dict(bg="#ede6d6", border="#e84e1b", label="#7a6f60",
                  levels=["#ddd3bd", "#f7b690", "#ff7a3d", "#e84e1b", "#a83a12"]),
}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

with urllib.request.urlopen(
    f"https://github-contributions-api.jogruber.de/v4/{USER}?y=last", timeout=30
) as r:
    data = json.load(r)

days = data["contributions"]
total = data["total"]["lastYear"]
first = date.fromisoformat(days[0]["date"])
# GitHub weeks start on Sunday; Python weekday(): Mon=0 .. Sun=6
offset = (first.weekday() + 1) % 7
weeks = (offset + len(days) + 6) // 7
width = LEFT + weeks * (CELL + GAP) - GAP + PAD
height = TOP + 7 * (CELL + GAP) - GAP + 26

for mode, t in THEMES.items():
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="Consolas, \'DejaVu Sans Mono\', Menlo, monospace">',
        f'<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="10" '
        f'fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="2"/>',
    ]
    seen_month = None
    for i, d in enumerate(days):
        day = date.fromisoformat(d["date"])
        slot = offset + i
        col, row = divmod(slot, 7)
        x = LEFT + col * (CELL + GAP)
        y = TOP + row * (CELL + GAP)
        svg.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="{RX}" '
            f'fill="{t["levels"][d["level"]]}"/>'
        )
        if day.month != seen_month and day.day <= 7 and row == 0:
            seen_month = day.month
            svg.append(
                f'<text x="{x}" y="{TOP-10}" font-size="11" '
                f'fill="{t["label"]}">{MONTHS[day.month-1]}</text>'
            )
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        y = TOP + row * (CELL + GAP) + CELL - 3
        svg.append(f'<text x="{PAD-6}" y="{y}" font-size="9" fill="{t["label"]}">{name}</text>')
    svg.append(
        f'<text x="{width-PAD}" y="{height-10}" font-size="11" text-anchor="end" '
        f'fill="{t["label"]}">{total:,} contributions in the last year</text>'
    )
    svg.append("</svg>")
    name = f"heatmap-{mode}.svg"
    with open(name, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print("wrote", name, f"({weeks} weeks, {total} contributions)")
