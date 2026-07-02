# footyIQ web

Next.js + Tailwind + shadcn/ui frontend for footyIQ, replacing the old Streamlit dashboard. Reads from the FastAPI backend in `../api/`.

## Run locally

The FastAPI backend must be running first (see the root README):

```bash
uvicorn api.main:app --reload --port 8000
```

Then, from this directory:

```bash
npm install
npm run dev
```

`NEXT_PUBLIC_API_URL` (see `.env.local`) points the app at the API — defaults to `http://localhost:8000`.

## Pages

- `/rankings` — season power rankings
- `/leaderboards` — category leaderboards (`?category=`)
- `/team-analysis` — single-team deep dive (`?team=`)
- `/matchups` — head-to-head projection + simulated round history (`?team_a=&team_b=`)

## Deploy

Deployed on Vercel with **Root Directory** set to `web/` and `NEXT_PUBLIC_API_URL` set to the deployed API's URL.
