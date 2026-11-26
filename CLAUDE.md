# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A tiny data-collection repo: a scraper (`fetch_gold.py`) that records the 24K/22K gold rates from https://www.pngjewellers.com/ into `gold_rates.csv`, run on a schedule by GitHub Actions, plus a static page (`index.html`) that charts that CSV and is meant to be hosted on GitHub Pages. There is no build system, test suite, linter config, or README.

## Commands

```bash
pip install requests beautifulsoup4   # the only dependencies (no requirements.txt)
python fetch_gold.py                  # scrape once; appends a row to gold_rates.csv and prints it
```

To view the chart locally, serve the repo root (`python3 -m http.server`) and open `/index.html`; opening the file directly fails because browsers block `fetch` on `file://`. Run the scraper from the repo root — the CSV path is relative (`gold_rates.csv`). Running locally appends a real row to the tracked CSV; `git checkout gold_rates.csv` to discard it.

## Architecture

- `fetch_gold.py` — fetches the page, finds `div.metal-pricing-popup` (falls back to whole-page text if that class changes), and regex-matches `24K Gold ₹<n>` / `22K Gold ₹<n>`. If a regex misses, the value is written as the literal string `"N/A"` rather than failing, so a site layout change shows up as `N/A` rows, not a red workflow run. Timestamps are generated in IST (UTC+05:30) and formatted `YYYY-MM-DD HH:MM:SS IST`.
- `.github/workflows/gold-rates.yml` — cron at `30 5,10 * * *` UTC (11:00 and 16:00 IST) plus `workflow_dispatch`. It runs the scraper, then commits and pushes `gold_rates.csv` as `github-actions[bot]` with the message "Update gold rates" (skipped if there's no diff). The git history is mostly these bot commits.
- `gold_rates.csv` — append-only log with header `Date,24ct,22ct`; prices are integers in ₹ (commas stripped).
- `index.html` — single self-contained file (inline CSS/JS, Plotly "basic" bundle from the cdn.plot.ly CDN, no build step). It tries `https://raw.githubusercontent.com/syamchandnair/goldie/main/gold_rates.csv` first (always current, but only reachable from a browser if the repo is public) and falls back to the relative `gold_rates.csv`. Default view is the 5 days before the *latest data point*; period buttons are custom (not Plotly's rangeselector) so ranges are deterministic, and the y-axis is refit to the visible window on every range change (see `onRelayout`). Lines use Plotly's `spline` shape, which can overshoot slightly between points; the markers are the real values.

## Things to know

- CSV schema/format is shared between the scraper, existing history and `index.html`'s parser; keep column order and the timestamp format stable if editing any of them. The page strips the ` IST` suffix and treats the rest as a plain wall-clock time (no timezone conversion), and treats `N/A` values as gaps in the line.
- Rows from 2026-01-01 through 2026-11-20 were backfilled with midnight timestamps (`00:00:00 IST`); live scraper rows (from 2026-11-21) carry real run times.
- Because the bot pushes to the default branch, pull/rebase before pushing local changes to avoid conflicts on `gold_rates.csv`.
