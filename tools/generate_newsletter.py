#!/usr/bin/env python3
"""
generate_newsletter.py
Renders research.json into a polished HTML newsletter + supporting files.

Usage:
    python tools/generate_newsletter.py .tmp/research.json
    python tools/generate_newsletter.py .tmp/research.json --infographics-dir .tmp/infographics

Outputs (all written to .tmp/archive/YYYY-MM-DD_<slug>/):
    newsletter.html     — CSS-inlined, email-safe HTML
    newsletter.txt      — Plain text fallback
    social_copy.md      — Subject line bank + LinkedIn/tweet copy
"""

import argparse
import base64
import json
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from premailer import transform


# ── Helpers ────────────────────────────────────────────────────────────────────

def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:50]


def _html_to_text(html: str) -> str:
    """Very lightweight HTML → plain text (no external deps)."""
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"</?(p|div|h[1-6]|li|tr)[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&[a-z]+;", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _embed_image(path: str) -> str:
    """Return a data-URI for a PNG so the HTML is fully self-contained."""
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{data}"


def _reading_time(data: dict) -> str:
    """Estimate reading time from section bodies."""
    words = 0
    for section in data.get("sections", []):
        words += len(section.get("body", "").split())
    for item in data.get("takeaways", []):
        words += len(item.split())
    minutes = max(1, round(words / 200))
    return f"~{minutes} min read"


# ── Archive directory ──────────────────────────────────────────────────────────

def _archive_dir(topic: str) -> Path:
    today = date.today().strftime("%Y-%m-%d")
    slug = _slugify(topic)
    path = Path(".tmp") / "archive" / f"{today}_{slug}"
    path.mkdir(parents=True, exist_ok=True)
    return path


# ── Social copy ────────────────────────────────────────────────────────────────

def _write_social_copy(data: dict, out_dir: Path):
    subject_lines = data.get("subject_lines", [])
    social = data.get("social", {})
    linkedin = social.get("linkedin", "")
    twitter = social.get("twitter", "")

    lines = [
        f"# Social Copy — {data['topic']}",
        f"\n_Generated {date.today().strftime('%B %d, %Y')}_\n",
        "---\n",
        "## Subject Lines (A/B Test Bank)\n",
    ]
    for i, subj in enumerate(subject_lines, 1):
        lines.append(f"{i}. {subj}")

    if linkedin:
        lines += ["\n---\n", "## LinkedIn Post\n", linkedin]
    if twitter:
        lines += ["\n---\n", "## Tweet\n", twitter]

    (out_dir / "social_copy.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✓ social_copy.md")


# ── Main render ────────────────────────────────────────────────────────────────

def render(research_path: str, infographics_dir: str | None = None) -> Path:
    with open(research_path, encoding="utf-8") as f:
        data = json.load(f)

    topic = data.get("topic", "Newsletter")
    archive = _archive_dir(topic)

    # Reading time (use JSON value if provided, else compute)
    reading_time = data.get("reading_time") or _reading_time(data)
    data["reading_time"] = reading_time

    # Preheader: use first stat or first sentence of summary
    if not data.get("preheader"):
        summary = data.get("summary", "")
        data["preheader"] = summary.split(".")[0].strip() + "."

    # Resolve infographic paths → embed as base64 data URIs
    if infographics_dir is None:
        infographics_dir = str(Path(research_path).parent / "infographics")

    chart_paths_raw = []
    if os.path.isdir(infographics_dir):
        chart_paths_raw = sorted(
            str(p) for p in Path(infographics_dir).glob("*.png")
        )

    # Embed images as data URIs so HTML is fully self-contained
    chart_paths_embedded = []
    for p in chart_paths_raw:
        try:
            chart_paths_embedded.append(_embed_image(p))
        except Exception as e:
            print(f"[WARN] Could not embed {p}: {e}", file=sys.stderr)

    # Format date
    today_str = datetime.now().strftime("%B %d, %Y")

    # Jinja2 render
    templates_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(str(templates_dir)), autoescape=False)
    template = env.get_template("newsletter.html.j2")

    raw_html = template.render(
        topic=topic,
        date=today_str,
        reading_time=reading_time,
        audience=data.get("audience", "general"),
        preheader=data.get("preheader", ""),
        summary=data.get("summary", ""),
        sections=data.get("sections", []),
        stats=data.get("stats", []),
        charts=data.get("charts", []),
        chart_paths=chart_paths_embedded,
        takeaways=data.get("takeaways", []),
        sources=data.get("sources", []),
    )

    # CSS inlining via Premailer (email safety)
    try:
        inlined_html = transform(raw_html, remove_classes=False, cssutils_logging_level=40)
    except Exception as e:
        print(f"[WARN] Premailer failed ({e}), using raw HTML", file=sys.stderr)
        inlined_html = raw_html

    # Write HTML
    html_path = archive / "newsletter.html"
    html_path.write_text(inlined_html, encoding="utf-8")
    print(f"  ✓ {html_path}")

    # Write plain text
    txt_path = archive / "newsletter.txt"
    txt_path.write_text(_html_to_text(inlined_html), encoding="utf-8")
    print(f"  ✓ {txt_path}")

    # Write social copy
    _write_social_copy(data, archive)

    # Symlink .tmp/latest → this archive
    latest = Path(".tmp") / "latest"
    if latest.is_symlink() or latest.exists():
        latest.unlink()
    try:
        latest.symlink_to(archive.resolve())
    except Exception:
        pass  # Windows fallback: just skip the symlink

    print(f"\nNewsletter ready → {archive}/")
    print(f"Quick open: open {html_path}")
    return archive


def main():
    parser = argparse.ArgumentParser(description="Render newsletter from research.json")
    parser.add_argument("research_json", help="Path to research.json")
    parser.add_argument("--infographics-dir", default=None, help="Directory of PNG charts")
    args = parser.parse_args()

    if not os.path.exists(args.research_json):
        print(f"Error: {args.research_json} not found", file=sys.stderr)
        sys.exit(1)

    render(args.research_json, args.infographics_dir)


if __name__ == "__main__":
    main()
