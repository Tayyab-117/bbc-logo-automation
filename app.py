import os
import shutil
import zipfile
import requests
import pandas as pd
import tempfile
from PIL import Image
from io import BytesIO
from flask import Flask, render_template, request, send_file, redirect, url_for, flash, send_from_directory
from add_logo import add_logo_to_image

app = Flask(__name__)
app.config['OUTPUT_FOLDER'] = 'output'

# Ensure output and uploads folders exist
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'xlsx'}

@app.route("/", methods=["GET", "POST"])
def index():
    languages = []
    logo_folder = os.path.join("static", "logos")
    if os.path.exists(logo_folder):
        languages = [name for name in os.listdir(logo_folder) if os.path.isdir(os.path.join(logo_folder, name))]
    processed = False
    download_ready = os.path.exists(app.config['OUTPUT_FOLDER']) and any(fname.lower().endswith((".png", ".jpg", ".jpeg")) for fname in os.listdir(app.config['OUTPUT_FOLDER']))

    if request.method == "POST":
        # Clear output dir
        if os.path.exists(app.config['OUTPUT_FOLDER']):
            shutil.rmtree(app.config['OUTPUT_FOLDER'])
        os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
        
        selected_language = request.form.get("language")
        # Construct the target directory
        logo_dir = os.path.join("static", "logos", selected_language, "Linear", "Web", "RGB")

        # Find any file ending with _HR_RGB.jpg in that folder
        logo_filename = None
        for fname in os.listdir(logo_dir):
            if fname.endswith("_HR_RGB.jpg"):
                logo_filename = fname
                break

        if logo_filename:
            logo_path = os.path.join(logo_dir, logo_filename)
        # Uploaded files
        uploaded_files = request.files.getlist("uploaded_files")
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = file.filename
                ext = os.path.splitext(filename)[1].lower()
                temp_dir = tempfile.mkdtemp()
                temp_path = os.path.join(temp_dir, filename)
                file.save(temp_path)
                if ext == ".xlsx":
                    try:
                        df = pd.read_excel(temp_path)
                        url_column = df.columns[0]
                        csv_urls = df[url_column].dropna().tolist()
                        for idx, url in enumerate(csv_urls):
                            try:
                                response = requests.get(url)
                                response.raise_for_status()
                                img = Image.open(BytesIO(response.content))
                                original_format = img.format or "JPEG"
                                if original_format.upper() == "JPEG":
                                    img = img.convert("RGB")
                                suffix = f".{original_format.lower()}"
                                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_img:
                                    img.save(tmp_img, format=original_format)
                                    tmp_img_path = tmp_img.name
                                add_logo_to_image(tmp_img_path, logo_path, selected_language)
                            except Exception as e:
                                flash(f"Failed to process URL from Excel: {url}\nError: {e}", "danger")
                    except Exception as e:
                        flash(f"❌ Error reading Excel file: {e}", "danger")
                elif ext in [".jpg", ".jpeg", ".png"]:
                    add_logo_to_image(temp_path, logo_path, selected_language)
                else:
                    flash(f"Unsupported file type: {file.filename}", "warning")
        
        # URLs from textarea
        url_input = request.form.get("url_input", "")
        if url_input.strip():
            urls = url_input.strip().splitlines()
            for idx, url in enumerate(urls):
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    img = Image.open(BytesIO(response.content))
                    original_format = img.format or "JPEG"
                    if original_format.upper() == "JPEG":
                        img = img.convert("RGB")
                    suffix = f".{original_format.lower()}"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_img:
                        img.save(tmp_img, format=original_format)
                        tmp_img_path = tmp_img.name
                    add_logo_to_image(tmp_img_path, logo_path, selected_language)
                except Exception as e:
                    flash(f"Failed to process URL: {url}\nError: {e}", "danger")

        processed = True
        download_ready = os.path.exists(app.config['OUTPUT_FOLDER']) and any(fname.lower().endswith((".png", ".jpg", ".jpeg")) for fname in os.listdir(app.config['OUTPUT_FOLDER']))

    if processed:
        # After processing and files are ready
        return redirect(url_for('index', download=1))
    return render_template("index.html", languages=languages, processed=processed, download_ready=download_ready)

@app.route('/download')
def download():
    # Create a zip of processed images
    output_dir = app.config['OUTPUT_FOLDER']
    zip_path = os.path.join(output_dir, "logo_stamped_images.zip")
    with zipfile.ZipFile(zip_path, "w") as zip_file:
        for fname in os.listdir(output_dir):
            fpath = os.path.join(output_dir, fname)
            if os.path.isfile(fpath) and fname != "logo_stamped_images.zip":
                zip_file.write(fpath, arcname=fname)
    return send_file(zip_path, as_attachment=True)

# To serve processed images individually if needed
@app.route('/output/<filename>')
def output_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)
