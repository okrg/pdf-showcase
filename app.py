import os
import uuid
import tempfile
from typing import List

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename

from pdf_preview.core import generate_preview, PDFValidationError

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Limit upload size to 25 MB (hard cap at server level)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html", error=None)

    # POST
    file = request.files.get("file")
    if not file or file.filename == "":
        return render_template("index.html", error="Please choose a PDF file to upload.")

    if not allowed_file(file.filename):
        return render_template("index.html", error="Only PDF files are allowed.")

    try:
        max_duration = float(request.form.get("max_duration", "10"))
    except ValueError:
        return render_template("index.html", error="Invalid max duration. Provide a number like 8 or 10.")

    fmt = request.form.get("format", "gif").lower()
    if fmt not in {"gif", "mp4"}:
        return render_template("index.html", error="Invalid format selected.")

    dimensions = request.form.get("dimensions", "480x640")

    # Save to temp dir
    unique_id = str(uuid.uuid4())
    upload_tmp_dir = tempfile.gettempdir()
    safe_name = secure_filename(file.filename)
    # Force .pdf extension
    if not safe_name.lower().endswith(".pdf"):
        safe_name += ".pdf"
    input_pdf_path = os.path.join(upload_tmp_dir, f"{unique_id}.pdf")
    file.save(input_pdf_path)

    # Generate outputs
    try:
        output_basename = os.path.join(OUTPUT_DIR, unique_id)
        outputs: List[str] = generate_preview(
            pdf_path=input_pdf_path,
            output_basename=output_basename,
            max_duration=max_duration,
            format=fmt,  # single format (UI offers gif or mp4)
            dimensions=dimensions,
        )
    except PDFValidationError as e:
        return render_template("index.html", error=str(e))
    except Exception as e:
        return render_template("index.html", error=f"Failed to generate preview: {e}")

    # Build filenames for rendering
    rel_files = [os.path.basename(p) for p in outputs]
    return render_template("result.html", files=rel_files, unique_id=unique_id)
    

@app.route("/downloads/<path:filename>")
def downloads(filename: str):
    # Serve generated files from OUTPUT_DIR
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=False)


if __name__ == "__main__":
    # For local development; use a production server for deployment
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)