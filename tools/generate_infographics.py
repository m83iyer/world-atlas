#!/usr/bin/env python3
"""
generate_infographics.py
Reads research.json, generates Plotly charts as PNG files.

Usage:
    python tools/generate_infographics.py .tmp/research.json
    python tools/generate_infographics.py .tmp/research.json --out .tmp/infographics
"""

import json
import os
import sys
import argparse
from pathlib import Path

import plotly.graph_objects as go
import plotly.io as pio


# ── Colour palette ─────────────────────────────────────────────────────────────
PALETTE = ["#2D3A8C", "#4A6CF7", "#7B9FF9", "#A8C0FB", "#D6E4FF"]
BG_COLOR = "#FFFFFF"
FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
FONT_COLOR = "#1A1A2E"

LAYOUT_DEFAULTS = dict(
    paper_bgcolor=BG_COLOR,
    plot_bgcolor=BG_COLOR,
    font=dict(family=FONT_FAMILY, color=FONT_COLOR, size=13),
    margin=dict(l=48, r=48, t=64, b=48),
    height=420,
    width=800,
)


def _apply_grid(fig):
    fig.update_xaxes(showgrid=False, linecolor="#E5E7EB", linewidth=1)
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#F3F4F6",
        gridwidth=1,
        linecolor="#E5E7EB",
        linewidth=1,
    )
    return fig


# ── Chart builders ─────────────────────────────────────────────────────────────

def build_bar(chart: dict) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=chart["labels"],
            y=chart["values"],
            marker_color=PALETTE[0],
            marker_line_width=0,
            text=[str(v) for v in chart["values"]],
            textposition="outside",
            textfont=dict(size=12, color=FONT_COLOR),
        )
    )
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text=chart["title"], font=dict(size=16, color=FONT_COLOR), x=0.04),
    )
    return _apply_grid(fig)


def build_horizontal_bar(chart: dict) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=chart["values"],
            y=chart["labels"],
            orientation="h",
            marker_color=PALETTE[:len(chart["labels"])],
            marker_line_width=0,
            text=[str(v) for v in chart["values"]],
            textposition="outside",
            textfont=dict(size=12, color=FONT_COLOR),
        )
    )
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text=chart["title"], font=dict(size=16, color=FONT_COLOR), x=0.04),
        yaxis=dict(autorange="reversed"),
    )
    return _apply_grid(fig)


def build_line(chart: dict) -> go.Figure:
    fig = go.Figure(
        go.Scatter(
            x=chart["labels"],
            y=chart["values"],
            mode="lines+markers",
            line=dict(color=PALETTE[0], width=3),
            marker=dict(size=8, color=PALETTE[1], line=dict(color=BG_COLOR, width=2)),
            fill="tozeroy",
            fillcolor="rgba(74,108,247,0.08)",
        )
    )
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text=chart["title"], font=dict(size=16, color=FONT_COLOR), x=0.04),
    )
    return _apply_grid(fig)


def build_pie(chart: dict) -> go.Figure:
    fig = go.Figure(
        go.Pie(
            labels=chart["labels"],
            values=chart["values"],
            marker=dict(colors=PALETTE, line=dict(color=BG_COLOR, width=2)),
            textinfo="label+percent",
            textfont=dict(size=13),
            hole=0.35,
        )
    )
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text=chart["title"], font=dict(size=16, color=FONT_COLOR), x=0.04),
        showlegend=True,
        legend=dict(orientation="v", x=1.02, y=0.5),
    )
    return fig


BUILDERS = {
    "bar": build_bar,
    "horizontal_bar": build_horizontal_bar,
    "line": build_line,
    "pie": build_pie,
}


# ── Main ───────────────────────────────────────────────────────────────────────

def generate(research_path: str, out_dir: str | None = None) -> list[str]:
    with open(research_path) as f:
        data = json.load(f)

    charts = data.get("charts", [])
    if not charts:
        print("No charts found in research.json — skipping infographics.")
        return []

    # Default output dir sits next to research.json
    if out_dir is None:
        base = Path(research_path).parent
        out_dir = str(base / "infographics")

    os.makedirs(out_dir, exist_ok=True)

    paths = []
    for i, chart in enumerate(charts):
        chart_type = chart.get("type", "bar").lower()
        builder = BUILDERS.get(chart_type, build_bar)

        try:
            fig = builder(chart)
        except Exception as e:
            print(f"[WARN] Chart {i} ({chart_type}) failed to build: {e}", file=sys.stderr)
            continue

        slug = chart["title"].lower().replace(" ", "_")[:40]
        filename = f"chart_{i+1:02d}_{slug}.png"
        out_path = os.path.join(out_dir, filename)

        try:
            pio.write_image(fig, out_path, scale=2)
            paths.append(out_path)
            print(f"  ✓ {out_path}")
        except Exception as e:
            print(f"[WARN] Could not write {out_path}: {e}", file=sys.stderr)

    print(f"\nGenerated {len(paths)} infographic(s) → {out_dir}")
    return paths


def main():
    parser = argparse.ArgumentParser(description="Generate infographics from research.json")
    parser.add_argument("research_json", help="Path to research.json")
    parser.add_argument("--out", default=None, help="Output directory for PNG files")
    args = parser.parse_args()

    if not os.path.exists(args.research_json):
        print(f"Error: {args.research_json} not found", file=sys.stderr)
        sys.exit(1)

    generate(args.research_json, args.out)


if __name__ == "__main__":
    main()
