# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

point_wx is a **Dash** (Plotly) multi-page weather web app. It pulls data from the [open-meteo](https://open-meteo.com/en/docs) REST APIs (plus Mapbox geocoding and OpenAI for AI reports/chatbot). The entrypoint is `src/app.py`, which exposes `server` (the underlying Flask app) for gunicorn. All API access goes through `src/utils/openmeteo_api.py`, and every response is cached with `flask-caching` (`@cache.memoize`).

## Commands

- Run dev server: `python src/app.py` — serves on `APP_PORT` (default 8083) at `URL_BASE_PATHNAME` (default `/pointwx/`), i.e. `http://localhost:8083/pointwx/`.
- Production: `cd src && gunicorn -b 127.0.0.1:8000 --workers=3 --timeout=90 --preload app:server`
- Docker: `docker build -t pointwx .` then `docker run -p 8083:8000 -e MAPBOX_KEY=... -e OPENMETEO_KEY=... pointwx`

There are **no tests and no linter configured**. The `*.ipynb` files at the repo root and in `src/` are exploratory/dev scratch, not part of the app.

## Environment variables

Read in `src/utils/settings.py`:

- `MAPBOX_KEY` — geocoding API (used by `src/utils/mapbox_api.py`).
- `OPENMETEO_KEY` — optional commercial open-meteo key. When set, `make_request()` rewrites request URLs to the `customer-` host and appends `apikey`; otherwise the free API is used.
- `OPENAI_KEY` — enables the AI report (`src/utils/ai_utils.py`) and the chatbot page.
- `OPENWEATHERMAP_KEY`, `APP_PORT`, `URL_BASE_PATHNAME`, `CACHE_DIR`, `DISABLE_CACHE`, and `REACT_VERSION` (must be `18.2.0` — required by dash-mantine).

## Architecture

### Per-page convention

Each subfolder in `src/pages/<page>/` is a self-registered Dash page (`dash.register_page(__name__, path=..., title=...)` in its `__init__.py`, enabled by `use_pages=True` in `app.py`). Follow this structure for a new page:

- `__init__.py` — registers the page, builds `layout`, and does `from .callbacks import *`, `from .figures import ...`, `from .options_selector import ...`.
- Layout (inline in `__init__.py` or a `layout.py`) — dbc/dmc components; typically a help `Accordion`, the shared `loc_selector`, an `opts_selector`, and a `dbc.Collapse` wrapping the figures with id `{"type": "fade", "index": "<page-name>"}`.
- `options_selector.py` — model/variable/day selectors.
- `callbacks.py` — a `@callback` fired by the pattern-matching submit button `{"type": "submit-button", "index": "<page>"}`; it reads the location Stores, calls a fetch function from `openmeteo_api`, and returns a figure to `{"type": "figure", "id": "<page>"}` plus the shared error-modal outputs.
- `figures.py` — pure Plotly figure builders.

Existing pages: `forecasts`, `forecasts_heatmap`, `ensemble`, `ensemble_heatmap`, `meteogram`, `vertical`, `model_climate`, `model_climate_daily`, `climate_calendar`, `chatbot`.

### Shared globals (`src/app.py`)

The `dcc.Store` components (`locations-list`, `location-selected`, `locations-favorites`, `client-details`, `client-first-visit`) are defined once in `serve_layout`. Cross-page callbacks (navbar active state, submit-button enable/disable, fade + scroll-to-figure) live here because they depend on the full `dash.page_registry`, which is only populated after the app initializes. New pages hook into these Stores and the pattern-matching id conventions rather than defining their own.

### Location selection

Shared across all pages via `src/components/location_selector.py` + `location_selector_callbacks.py`, which populate the `locations-list` / `location-selected` Stores that every page's callback reads.

### URL state synchronization

`src/utils/url_sync.py` maintains bidirectional sync between URL query parameters and app state via clientside callbacks. Changes to location/model/variable selections update the URL (using `history.replaceState`), and URL changes (back/forward navigation, direct links) restore app state. This enables shareable deep links to specific forecasts.

### Location-aware model filtering

When a user selects a location, available models are automatically filtered based on their geographic coverage domains. This ensures users only see models that provide data for their selected location. The filtering logic:
- `src/utils/model_domains.py` — defines geographic bounding boxes for each model
- `src/utils/location_model_filter.py` — callback factory to avoid duplicating filtering logic across pages
- Applied on pages: `forecasts`, `forecasts_heatmap`, `ensemble`, `ensemble_heatmap`, `meteogram`, `vertical`

### Data layer (`src/utils/openmeteo_api.py`)

The single source of API access (~1200 lines): `get_forecast_data`, `get_ensemble_data`, `get_historical_data`, `compute_climatology`, and many more, each `@cache.memoize`d with a TTL appropriate to how often the data changes. Add new data access here, not in page callbacks.

### Settings hub (`src/utils/settings.py`)

Holds the `cache` object, all env vars, and the Plotly theme configuration. Model/variable option lists have been moved to `src/utils/constants/`.

### Constants (`src/utils/constants/`)

Organized constants module with separated concerns:
- `ensemble.py` — `ENSEMBLE_MODELS`, `ENSEMBLE_VARS`
- `deterministic.py` — `DETERMINISTIC_MODELS`, `DETERMINISTIC_VARS`
- `reanalysis.py` — `REANALYSIS_MODELS`, `REANALYSIS_VARS`
- `climatology.py` — climatology-related constants
- `seasonal.py` — seasonal forecast constants
- `domains.py` — model geographic coverage domains
- `model_metadata.py` — model metadata and initialization times
- `plotly_config.py` — Plotly image export configuration

### AI features

`src/utils/ai_utils.py` (exposed via the `/report` Flask route in `app.py`) and `src/pages/chatbot/functions.py` define OpenAI tool/function-calling helpers that themselves call the `openmeteo_api` layer.

### Plotly theme

A custom template named `"custom"` is defined in `src/utils/custom_theme.py` and set as the default in `settings.py`.

### Caching (`src/utils/openmeteo_api.py`)

- TTL strategy: forecast data ~10 min, historical ~24h, climatology ~7 days
- Clear cache: delete files in `CACHE_DIR` (default `.cache/`) or set `DISABLE_CACHE=1`
- All API responses are memoized to avoid redundant requests

### Pattern-matching IDs (cross-page)

- `{"type": "submit-button", "index": "<page>"}` — triggers data fetch
- `{"type": "fade", "index": "<page>"}` — wraps figures for fade-in animation
- `{"type": "figure", "id": "<page>"}` — target for figure output

## Implementation patterns

### Typical callback flow

1. User fills location + options selectors
2. Pattern-matching submit button fires page callback
3. Callback reads `locations-list`/`location-selected` Stores + page option values
4. Calls fetch function from `openmeteo_api.py` (auto-cached)
5. Transforms response → calls figure builder from `figures.py`
6. Returns figure + error-modal outputs (always return both, using `allow_duplicate=True`)

### Component libraries

- **dash-bootstrap-components (dbc)**: Layout (Container, Row, Col), Cards, Modals, Navbar, Accordion — most structural components
- **dash-mantine-components (dmc)**: Form inputs (Select, MultiSelect, DatePicker, SegmentedControl, NumberInput) — richer interactivity and styling
- Both can mix freely; dmc requires `REACT_VERSION=18.2.0`

### Store usage

- **Global Stores** (in `app.py`): `locations-list`, `location-selected`, `locations-favorites`, `client-details`, `client-first-visit` — read by all pages
- **Page-local Stores**: Use sparingly; prefer direct callback outputs when data doesn't need to persist across navigation
- **DataFrame serialization**: `df.to_json(orient="split")` → Store → `pd.read_json(StringIO(json_str), orient="split")` (preserves dtypes, smaller than records)

### Multi-page routing

- Each page's `path=` in `dash.register_page()` is appended to `URL_BASE_PATHNAME`
- Example: `path="/forecasts"` → `http://localhost:8083/pointwx/forecasts`
- Homepage is registered with `path="/"` → `http://localhost:8083/pointwx/`
- `dash.page_registry` (available after app init) holds all registered pages

### Performance

- `prevent_initial_call=True` on most callbacks (avoid firing on page load with no data)
- Pattern-matching callbacks centralized in `app.py` minimize duplication
- Large datasets: keep figure data transforms in `openmeteo_api.py` layer, not in callbacks
- Loading states: use dmc.LoadingOverlay or dbc.Spinner around `Collapse` wrappers

## Conventions

- DataFrames are passed between callbacks as JSON through `dcc.Store` and re-read with `pd.read_json(StringIO(...), orient="split")`.
- Errors surface through the shared `error-modal` / `error-message` outputs (using `allow_duplicate=True`), not raised exceptions.
- When testing add `from app import app` (even if you're not running the app) at the top of every script to properly initialize the cache
