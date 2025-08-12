import os
from flask import Flask, request, jsonify, send_file, Response
from PIL import Image
from io import BytesIO
import zipfile
import requests
import mimetypes
import traceback
from add_logo_util import paste_logo

app = Flask(__name__)

BASES = [
    os.getcwd(),
    os.path.join(os.path.dirname(__file__), ".."),
    os.path.dirname(__file__),
]
def _resolve_logos_root():
    for base in BASES:
        cand = os.path.abspath(os.path.join(base, 'logos'))
        if os.path.isdir(cand):
            return cand
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logos'))
LOGOS_ROOT = _resolve_logos_root()

def find_logo_for_language(language: str):
    """
    Find the first .png under logos/<language> recursively.
    Fall back to .jpg when .png is not present.
    Returns an open PIL Image.
    """
    if not language:
        raise ValueError("language is required")

    lang_folder = os.path.join(LOGOS_ROOT, language)
    if not os.path.isdir(lang_folder):
        raise FileNotFoundError(f"Language folder not found: {lang_folder}")

    # Prefer files that end with '_RGB.png' (as in your assets),
    # then any .png, then .jpg/.jpeg.
    preferred_png = None
    any_png = None
    any_jpg = None
    for root, dirs, files in os.walk(lang_folder):
        for name in files:
            lower = name.lower()
            full = os.path.join(root, name)
            if lower.endswith("_rgb.png") and preferred_png is None:
                preferred_png = full
            elif lower.endswith(".png") and any_png is None:
                any_png = full
            elif lower.endswith((".jpg", ".jpeg")) and any_jpg is None:
                any_jpg = full
    path = preferred_png or any_png or any_jpg
    if not path:
        raise FileNotFoundError(f"No logo image found under: {lang_folder}")
    return Image.open(path)

def read_image_from_request_file(file_storage):
    data = file_storage.read()
    return Image.open(BytesIO(data)), file_storage.filename or "upload.jpg"

def read_image_from_url(url: str):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return Image.open(BytesIO(r.content)), os.path.basename(url.split("?")[0]) or "remote.jpg"

def safe_name(base: str, language: str):
    root, ext = os.path.splitext(base)
    if not ext:
        ext = ".jpg"
    return f"{root}_{language}{ext}"

@app.route("/api/add_logo", methods=["POST"])
def add_logo():
    try:
        language = request.form.get("language")
        logo_scale = float(request.form.get("logo_scale", "0.40"))
        if not language:
            return jsonify({"error": "language is required"}), 400

        # Resolve logo once
        logo_img = find_logo_for_language(language)

        # Collect images from files and urls
        images_to_process = []

        # Multiple local files
        for key in request.files:
            if key == "excel":
                continue
            file_storage = request.files.getlist(key)
            for fs in file_storage:
                try:
                    img, fname = read_image_from_request_file(fs)
                    images_to_process.append((img, fname))
                except Exception:
                    pass

        # URLs from form fields
        urls = request.form.getlist("url")
        for u in urls:
            if not u.strip():
                continue
            img, fname = read_image_from_url(u.strip())
            images_to_process.append((img, fname))

        # Excel with URLs (optional)
        if "excel" in request.files:
            try:
                from openpyxl import load_workbook
                excel_fs = request.files["excel"]
                wb = load_workbook(excel_fs, read_only=True, data_only=True)
                ws = wb.active
                headers = []
                if ws.max_row >= 1:
                    headers = [ (c.value or "").strip().lower() if isinstance(c.value, str) else c.value for c in next(ws.iter_rows(min_row=1, max_row=1)) ]
                url_col_idx = None
                if headers:
                    for idx, h in enumerate(headers):
                        if h in ("url", "image_url"):
                            url_col_idx = idx + 1
                            break
                # If headers not found, default to first column
                if url_col_idx is None:
                    url_col_idx = 1
                for row in ws.iter_rows(min_row=2 if headers else 1):
                    cell = row[url_col_idx-1].value
                    if not cell:
                        continue
                    u = str(cell).strip()
                    if not u:
                        continue
                    try:
                        img, fname = read_image_from_url(u)
                        images_to_process.append((img, fname))
                    except Exception:
                        continue
            except Exception:
                # ignore excel errors but continue
                pass

        if not images_to_process:
            return jsonify({"error": "No images provided. Upload files or supply URLs or Excel."}), 400

        outputs = []
        for img, fname in images_to_process:
            composed = paste_logo(img, logo_img, language, logo_scale=logo_scale)
            out = BytesIO()
            # Save using source extension to preserve format when possible
            ext = (os.path.splitext(fname)[1] or ".jpg").lower()
            if ext in [".png"]:
                composed.convert("RGBA").save(out, format="PNG", optimize=True)
                out.seek(0)
                outputs.append((safe_name(fname, language), "image/png", out))
            else:
                composed.convert("RGB").save(out, format="JPEG", quality=100, optimize=True)
                out.seek(0)
                outputs.append((safe_name(fname, language).rsplit(".",1)[0] + ".jpg", "image/jpeg", out))

        if len(outputs) == 1:
            name, mime, bio = outputs[0]
            return send_file(bio, mimetype=mime, as_attachment=True, download_name=name)

        # multiple files → zip
        zip_buf = BytesIO()
        with zipfile.ZipFile(zip_buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for name, mime, bio in outputs:
                zf.writestr(name, bio.getvalue())
        zip_buf.seek(0)
        return send_file(zip_buf, mimetype="application/zip", as_attachment=True, download_name="logo_stamped_images.zip")

    except Exception as e:
        tb = traceback.format_exc()
        print('FUNCTION ERROR', e, tb, flush=True)
        return Response(f"Error: {e}\n\n{tb}", status=500, mimetype="text/plain")

# For local testing: `python api/add_logo.py`
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
