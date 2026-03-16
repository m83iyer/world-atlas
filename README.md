# 🌍 World Atlas — Interactive Country Explorer

A polished, single-file interactive world map that lets you explore key facts about every country on Earth. Built with Leaflet.js and vanilla JavaScript — no build step, no framework, no backend.

---

## Preview

> Hover or click any country to highlight it, mute the rest, and reveal a rich info panel with flag, capital, population, cities, languages, and currency data.

---

## Features

- 🗺️ **Full world political map** with country borders and zoom/pan
- 🖱️ **Hover to preview** — active country pops forward, everything else fades
- 📌 **Click to pin** — card stays open as you move around the map
- 📋 **Country flashcard** — flag, continent, capital, population, top cities, languages, currency
- 🌐 **~195 countries** covered — every UN member state + Taiwan
- 📱 **Responsive** — right-side panel on desktop, bottom sheet on mobile
- ⚡ **Zero dependencies** to install — opens straight in the browser

---

## Getting Started

### Run locally

No server required. Just open the file:

```bash
open index.html
```

Or double-click `index.html` in Finder.

> **Requires internet** for two CDN resources on first load:
> - Leaflet 1.9.4 (unpkg.com)
> - World GeoJSON — Natural Earth via datasets/geo-countries (raw.githubusercontent.com)

---

## Project Structure

```
world-atlas/
├── index.html          # Complete app — HTML + CSS + JS in one file
└── README.md
```

### Inside `index.html`

| Section | Purpose |
|---|---|
| CSS custom properties | Design tokens — change 6 variables to retheme the whole app |
| `COUNTRY_DATA` | ~195 country fact objects, keyed by ISO Alpha-2 code |
| `STYLES` | Three Leaflet style presets: default / active / muted |
| Map init | Leaflet setup, zoom controls, world bounds |
| GeoJSON fetch | Loads world polygons from CDN, builds `layersByCode` lookup |
| Event handlers | Hover, mouse-out, click, map-click state machine |
| `updateStyles()` | Iterates all layers and applies the correct style |
| `updatePanel()` | Renders the flashcard HTML into the info panel |

---

## Interaction Model

```
Hover country  →  preview mode  →  panel slides in
Mouse out      →  panel closes  (unless pinned)
Click country  →  pin mode      →  panel stays open
Click again    →  unpin         →  panel closes
Click ocean    →  unpin         →  panel closes
```

---

## Expanding the Dataset

### Add a country

Append an entry to the `COUNTRY_DATA` object in `index.html`. Use any ISO Alpha-2 code as the key:

```js
"PT": {
  name: "Portugal",
  continent: "Europe",
  capital: "Lisbon",
  top_cities: ["Lisbon", "Porto", "Braga"],
  population: "10.3 million",
  languages: ["Portuguese", "Mirandese", "English"],
  currency_name: "Euro",
  currency_code: "EUR",
  currency_value_note: "1 EUR ≈ 1.08 USD",
  flag_emoji: "🇵🇹"
}
```

No other code changes needed.

### Split into separate files (production setup)

| File | Contains |
|---|---|
| `index.html` | HTML skeleton only |
| `styles.css` | All CSS (cut from `<style>` block) |
| `script.js` | All JS (cut from `<script>` block) |
| `countries.json` | `COUNTRY_DATA` object — fetch with `fetch('./countries.json')` |
| `world.geojson` | Download from datasets/geo-countries and serve locally |

### Add live exchange rates

Replace the static `currency_value_note` field with a live lookup:

```js
fetch('https://open.er-api.com/v6/latest/USD')
  .then(r => r.json())
  .then(data => {
    var rate = (1 / data.rates[countryData.currency_code]).toFixed(4);
    // display as "1 USD = X [CODE]"
  });
```

---

## Roadmap

- [ ] Country search box
- [ ] Continent filter
- [ ] Dark mode
- [ ] Zoom to country on click
- [ ] Live exchange rates via open.er-api.com
- [ ] Country comparison mode
- [ ] Export country card as image
- [ ] Full offline mode (local GeoJSON)
- [ ] Keyboard accessibility (tab, Enter, Escape)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Map engine | [Leaflet 1.9.4](https://leafletjs.com) |
| Map data | [Natural Earth via geo-countries](https://github.com/datasets/geo-countries) |
| Language | Vanilla JavaScript (ES5-compatible) |
| Styling | CSS custom properties, no preprocessor |
| Fonts | System UI stack — no external font CDN |

---

## License

MIT — free to use, modify, and distribute.
