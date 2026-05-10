# Secondhand Feed

Local Docker app for a curated secondhand clothing feed: hexagonal FastAPI backend, Next.js UI, SQLite persistence, YAML buyer profile.

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

- App: http://localhost:3000
- API health: http://localhost:8000/health

Use **Run fake source** on the feed page to import fixture listings, score them, and populate the feed. Edit preferences under **Profile** (`data/buyer_style_profile.yaml` on disk).

## Optional live eBay listings

Create an eBay developer application and set **client credentials** (no user login required for public search):

1. Add to `.env`:
   - `EBAY_CLIENT_ID`
   - `EBAY_CLIENT_SECRET`
   - `EBAY_MARKETPLACE_ID=EBAY_US` (default)
2. Rebuild/restart: `docker compose up --build`
3. On the feed page, use **Run eBay search** (query + limit). Results go through the same normalize → score → feed pipeline as the fake source.

If credentials are unset, only the fake source is available.

## Architecture

- **Domain**: pure normalization and scoring (no FastAPI/DB).
- **Application**: use cases orchestrating ports.
- **Adapters**: SQLite repos, YAML profile store, source connectors.
- **BFF**: thin FastAPI routes and presenters.

## Development without Docker

**Backend**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
export DATA_DIR=../data DATABASE_PATH=../data/app.db PROFILE_PATH=../data/buyer_style_profile.yaml
uvicorn app.main:app --reload --port 8000
```

**Frontend**

```bash
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

**Tests**

```bash
cd backend && pytest -q
```
