# Logo stamper on vercel

- Static `index.html` served from project root.
- Python endpoints as Vercel Functions under `/api`.
- Logos bundled via `includeFiles` and resolved robustly at runtime.

## endpoints
- `GET /api/health` → quick runtime check
- `GET /api/languages` → scans `/logos/*`
- `POST /api/add_logo` → files/urls/excel → image or zip

## deploy
- Push this folder to GitHub (files, not a .zip)
- Import in Vercel → Framework: **Other**, no build, no output dir
- If your repo has a wrapper folder, set **Root Directory** accordingly
