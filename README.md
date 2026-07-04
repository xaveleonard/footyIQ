# footyIQ

Fantasy league analytics and matchup dashboard, built with a Python/FastAPI backend and a Next.js frontend.

## Features

- Power rankings
- Category leaderboards
- Head-to-head matchup analysis
- Recent form tracking
- Volatility / consistency metrics
- Responsive dashboard (desktop + mobile)

## Tech Stack

- **Backend**: Python, Pandas, FastAPI
- **Frontend**: Next.js, TypeScript, Tailwind CSS, shadcn/ui
- **Data**: Parquet, scraped via Selenium
- **Hosting**: Render (API), Vercel (web)

## Project Structure

```
analysis/     - analytics/rankings/matchup engines (pure pandas, framework-agnostic)
api/          - FastAPI backend serving JSON over analysis/
web/          - Next.js frontend
pipeline/     - Selenium scraper that populates data/
scripts/      - one-off diagnostic scripts
data/         - raw parquet datasets
tests/        - unit tests (analysis/) and API tests (api/)
```

## Run Locally

Backend (from the repo root):

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # fill in values if running pipeline/scraper.py
uvicorn api.main:app --reload --port 8000
```

Frontend (in a separate terminal):

```bash
cd web
npm install
npm run dev
```

The web app expects the API at `http://localhost:8000` by default (see `web/.env.local`).

## Tests

```bash
pytest
```

## Deploy

- **API**: Render, via `render.yaml` (Root Directory: repo root)
- **Web**: Vercel (Root Directory: `web/`, env var `NEXT_PUBLIC_API_URL` pointing at the deployed API)

CORS on the API is controlled by the `ALLOWED_ORIGINS` env var (comma-separated).

## Updating Data

```bash
python -m pipeline.scraper
```

Scrapes new rounds incrementally, stopping automatically at the first round that hasn't been played yet. Commit and push the updated parquet files, then redeploy the API on Render to pick up the new data.

To backfill or re-scrape specific rounds instead (e.g. after a round finishes but before the next one does, or to fix a round that scraped with bad data), pass `--rounds`:

```bash
python -m pipeline.scraper --rounds 14 15 16
```

This replaces any existing data for those exact rounds rather than appending alongside it.
