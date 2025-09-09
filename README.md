# PDF Preview Animator Tool

Generate a short animated preview from a PDF as a GIF or MP4. Available via CLI and a simple Flask web interface.

## Features

- PDF processing with PyMuPDF (fitz)
- Animation generation with MoviePy
- Smooth crossfade transitions
- CLI and Web UI
- Configurable output format, duration, and dimensions
- Temporary outputs with a daily cleanup recommendation

---

## Requirements

- Python 3.8+
- System ffmpeg is recommended for better performance/compatibility
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt-get install -y ffmpeg`
  - Windows (chocolatey): `choco install ffmpeg`

## Install

```bash
# Clone the repo and enter it
git clone https://github.com/okrg/pdf-showcase.git
cd pdf-showcase

# Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## CLI Usage

```bash
python generate.py report.pdf --output my_preview --max-duration 8 --format mp4 --dimensions 480x640
```

Arguments:

- `input_file`: Required positional argument (path to PDF).
- `--output`: Base name for the output (no extension). Default: `<input_basename>_preview` in CWD.
- `--max-duration`: Maximum length in seconds (default: 10).
- `--format`: `gif`, `mp4`, or `all` (default: `gif`).
- `--dimensions`: `WIDTHxHEIGHT` string (default: `480x640`).

Validation rules:

- Max file size: 25 MB
- Max page count: 100 pages

When the PDF is longer than the maximum duration allows (with a minimum per-page display time of 0.4s), the tool samples pages evenly, always including the first and last pages.

---

## Web App

Run locally:

```bash
export FLASK_APP=app.py
export FLASK_ENV=development  # optional; enables debug auto-reload
python app.py
# Then open http://localhost:5000
```

- Upload a PDF, choose format, duration, and dimensions.
- Results are shown with inline preview and download links.
- Files are written to the `output/` directory.

Server-side limits:

- Uploads larger than 25 MB are rejected.
- Input PDFs with more than 100 pages are rejected.

---

## Temporary File Cleanup

Generated files should be cleaned up after 24 hours. The simplest approach: a daily cron job.

Example (Linux/macOS):

```bash
# Create a cleanup script (already present at scripts/cleanup.sh)
chmod +x scripts/cleanup.sh

# Edit crontab
crontab -e

# Add a line to run it daily at midnight (adjust the path accordingly)
0 0 * * * /bin/bash /absolute/path/to/pdf-showcase/scripts/cleanup.sh
```

`scripts/cleanup.sh` does:

```bash
# Deletes files older than 24 hours from output/
find /absolute/path/to/pdf-showcase/output -type f -mtime +0 -delete
```

Note: `-mtime +0` targets files older than 24 hours.

Windows Task Scheduler alternative:

- Create a basic task that runs daily and executes:
  - `powershell.exe -ExecutionPolicy Bypass -File "C:\path\to\pdf-showcase\scripts\cleanup.ps1"`
- Example PowerShell script (`scripts/cleanup.ps1`):
  ```powershell
  Get-ChildItem "C:\path\to\pdf-showcase\output" -File | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-1) } | Remove-Item -Force
  ```

---

## Development Notes

- Core function: `pdf_preview.core.generate_preview(pdf_path, output_basename, max_duration, format, dimensions, ...)`
- Crossfade duration defaults to 0.15s. Minimum per-page display time is 0.4s.
- MP4 is encoded with H.264 (`libx264`) at 24 fps, GIF at 15 fps.
- The renderer pads images to match the desired output dimensions while preserving aspect ratio.

---

## Troubleshooting

- If MP4 export fails, ensure `ffmpeg` is installed and discoverable on your PATH.
- For very large PDFs, use the CLI to pre-trim or decrease dimensions to reduce processing requirements.
- If you see validation errors for size or page count, reduce your PDF accordingly.

---

## License

MIT