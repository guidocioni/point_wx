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

### Data layer (`src/utils/openmeteo_api.py`)

The single source of API access (~1200 lines): `get_forecast_data`, `get_ensemble_data`, `get_historical_data`, `compute_climatology`, and many more, each `@cache.memoize`d with a TTL appropriate to how often the data changes. Add new data access here, not in page callbacks.

### Settings hub (`src/utils/settings.py`)

Holds the `cache` object, all env vars, the Plotly `images_config`, and the large model/variable option lists (`ENSEMBLE_MODELS`, `ENSEMBLE_VARS`, `DETERMINISTIC_MODELS`, `DETERMINISTIC_VARS`, `REANALYSIS_MODELS`, ...) reused by the page selectors.

### AI features

`src/utils/ai_utils.py` (exposed via the `/report` Flask route in `app.py`) and `src/pages/chatbot/functions.py` define OpenAI tool/function-calling helpers that themselves call the `openmeteo_api` layer.

### Plotly theme

A custom template named `"custom"` is defined in `src/utils/custom_theme.py` and set as the default in `settings.py`.

## Conventions

- DataFrames are passed between callbacks as JSON through `dcc.Store` and re-read with `pd.read_json(StringIO(...), orient="split")`.
- Errors surface through the shared `error-modal` / `error-message` outputs (using `allow_duplicate=True`), not raised exceptions.
- Whenever a modification to the code needs to be implemented, isolate the function/code in a test script and perform all tests there before implementing in the main code. Remember to import the app cache so that the data fetching functions work flawlessly.
