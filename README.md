# Logo Stamper on Vercel

This project exposes a Python API that stamps a language-specific logo onto images. It runs as Vercel Functions and ships with a static upload page.

## Endpoints

- `GET /api/languages` → JSON list of available languages pulled from the `logos/` folder
- `POST /api/add_logo` → Accepts images and returns a processed image or a ZIP if multiple

## Inputs

You can provide any combination of:
- `images`: one or many image files (PNG or JPEG)
- `url`: one or many URL fields pointing to images online
- `excel`: an `.xlsx` file that contains a first column of URLs or a column named `url` or `image_url`
- `language`: required, matches a folder name under `logos/`
- `logo_scale` (optional): a float fraction of image width, default 0.40

## Output

- If one image is processed, the response is an image with `Content-Disposition: attachment`
- If more than one image is processed, the response is a ZIP containing all results

## Assets

Place your logo assets like this:
```
logos/
  Nepali/...
  Punjabi/...
  Urdu/...
```
The server will pick the first `.png` it finds under a language. It falls back to `.jpg` if there is no `.png`.

## Local dev

```bash
pip install -r requirements.txt
cd api
python add_logo.py  # provides a local Flask server at http://127.0.0.1:5000
```

Then open `index.html` in a browser and change the API base URL if needed.

## Deploy

- Push to a GitHub repo with this folder structure
- Import into Vercel and deploy
- Ensure the `logos/` directory is present in the project root in your main branch
