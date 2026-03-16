# Newsletter Automation Workflow

## Objective
Generate a polished, email-safe HTML newsletter on any topic — complete with research, data-driven
infographic charts, a subject line bank, plain text version, and social copy. Output is saved locally
to `.tmp/archive/YYYY-MM-DD_<slug>/`.

## Required Inputs
| Input | Type | Example |
|---|---|---|
| `topic` | string | `"AI in Healthcare 2025"` |
| `audience` | `general` \| `technical` \| `executive` | `"general"` (default) |

## Execution Steps

### Step 1 — Research (Claude, using WebSearch + WebFetch)

Run **5–7 web searches** across these angles:
- Latest news and developments (last 6 months)
- Key statistics and market data
- Major players / companies / people
- Trends and forecasts
- Controversies or challenges

Fetch the **full content** of 3–5 high-value URLs. Prioritise:
- Industry reports, research papers
- Reputable news sources
- Official company/org announcements

Flag any source whose publication date is older than 90 days as `"fresh": false`.

### Step 2 — Structure research into JSON

Write findings to `.tmp/research.json` using this exact schema:

```json
{
  "topic": "string",
  "audience": "general | technical | executive",
  "summary": "2–3 sentence executive summary of the entire newsletter",
  "preheader": "Single sentence shown in email clients as preview text (different from summary)",
  "reading_time": "~N min read",
  "sections": [
    {
      "title": "Section heading",
      "body": "Full paragraphs. Separate paragraphs with a blank line (\\n\\n).",
      "pull_quote": "Optional standout quote or stat from this section (or empty string)"
    }
  ],
  "stats": [
    {
      "label": "Short label (3–5 words)",
      "value": "Display value (e.g. $4.2T or 68%)",
      "context": "One line of context"
    }
  ],
  "charts": [
    {
      "type": "bar | horizontal_bar | line | pie",
      "title": "Chart title",
      "labels": ["Label A", "Label B"],
      "values": [42, 87]
    }
  ],
  "takeaways": [
    "Concise actionable or insight string",
    "..."
  ],
  "subject_lines": [
    "Subject line option 1",
    "Subject line option 2",
    "Subject line option 3",
    "Subject line option 4",
    "Subject line option 5"
  ],
  "social": {
    "linkedin": "Full LinkedIn post copy (150–300 words)",
    "twitter": "Tweet copy (max 280 chars)"
  },
  "sources": [
    {
      "url": "https://...",
      "title": "Source title",
      "date": "YYYY-MM-DD or Month YYYY",
      "fresh": true
    }
  ]
}
```

**Quality bar for research.json:**
- `sections`: aim for 3–5, each with 150–300 words of body copy
- `stats`: exactly 3 (fills the stat bar row in the template)
- `charts`: 2–3 charts with real data extracted from sources
- `subject_lines`: exactly 5, each using a different hook (curiosity / urgency / data / question / bold claim)
- `takeaways`: 4–6 punchy bullets

### Step 3 — Generate infographics

```bash
python tools/generate_infographics.py .tmp/research.json
```

Charts are saved to `.tmp/infographics/chart_NN_<slug>.png`.

Supported chart types:
- `bar` — vertical bar chart
- `horizontal_bar` — ranked list style
- `line` — trend over time
- `pie` — share/composition (use sparingly)

If a chart fails to generate, remove it from `research.json["charts"]` and re-run,
or continue — missing charts are handled gracefully by the renderer.

### Step 4 — Render newsletter

```bash
python tools/generate_newsletter.py .tmp/research.json
```

Outputs written to `.tmp/archive/YYYY-MM-DD_<topic-slug>/`:
| File | Description |
|---|---|
| `newsletter.html` | Premailer CSS-inlined HTML, self-contained (images embedded as base64) |
| `newsletter.txt` | Plain text fallback for email deliverability |
| `social_copy.md` | 5 subject lines + LinkedIn post + tweet |

`.tmp/latest/` is symlinked to the most recent archive for quick access.

### Step 5 — Report to user

Tell the user:
1. The archive path
2. How to open: `open .tmp/latest/newsletter.html`
3. Print the 5 subject lines from `social_copy.md` so they can pick one immediately

---

## Edge Cases

| Situation | Action |
|---|---|
| Topic is too broad (e.g. "technology") | Ask user to narrow to a sub-topic before researching |
| Web search returns sparse results | Broaden to related angles; note gaps in the newsletter's sources section |
| A chart fails (Kaleido not installed) | Run `pip install kaleido` and retry; skip that chart if still failing |
| Premailer CSS inlining fails | Newsletter still renders; warn user to test in email client manually |
| Fewer than 3 stats found | Use 1–2 stats; leave remaining stat cells blank rather than fabricating data |

## Dependencies

Install once:
```bash
pip install -r requirements.txt
```

Required packages: `jinja2`, `plotly`, `kaleido`, `premailer`, `Pillow`

## Output Quality Checklist

- [ ] Opens correctly in browser (Chrome/Safari)
- [ ] Mobile layout looks correct (DevTools → responsive mode, 375px)
- [ ] Dark mode adapts (enable OS dark mode, reload)
- [ ] Plain text is readable without HTML
- [ ] Subject lines use varied hooks (not all the same style)
- [ ] All sources are linked and dated
- [ ] Stale sources (>90 days) are flagged in the HTML banner
