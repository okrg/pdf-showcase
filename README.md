# PDF Preview Animator Tool

Generate a short animated preview from a PDF as a GIF or MP4. Available via CLI and a simple Flask web interface.

## Features

- PDF processing with PyMuPDF (fitz)
- Animation generation with MoviePy
- **Bright, smooth crossfade transitions** using CrossFadeIn for professional-looking page transitions
- CLI and Web UI
- Configurable output format, duration, and dimensions
- White background preservation during transitions (no dark flashes)
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
python generate.py report.pdf --output my_preview --max-duration 8 --format mp4 --size large
```

Arguments:

- `input_file`: Required positional argument (path to PDF).
- `--output`: Base name for the output (no extension). Default: `<input_basename>_preview` in CWD.
- `--max-duration`: Maximum length in seconds (default: 10).
- `--format`: `gif`, `mp4`, or `all` (default: `gif`).
- `--size`: Output size preset: `small` (320×480), `medium` (480×640), `large` (720×960) (default: `medium`).
- `--crossfade`: Crossfade duration between pages in seconds (default: 0.15). Uses bright CrossFadeIn transitions.

Validation rules:

- Max file size: 25 MB
- Max page count: 100 pages

**Crossfade Quality:** The tool uses MoviePy's `CrossFadeIn` effect for smooth, bright transitions between pages. This prevents the dark flashing that can occur with standard fade effects, maintaining a professional appearance with consistent white background visibility.

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

- Upload a PDF, choose format, duration, and size preset.
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

- Core function: `pdf_preview.core.generate_preview(pdf_path, output_basename, max_duration, format, dimensions, crossfade, ...)`
- **Size presets:** "small" (320×480), "medium" (480×640), "large" (720×960). Custom dimensions still supported for backward compatibility.
- **Crossfade implementation:** Uses `moviepy.vfx.CrossFadeIn` for bright, professional transitions. Default duration is 0.15s.
- Minimum per-page display time is 0.4s.
- MP4 is encoded with H.264 (`libx264`) at 24 fps, GIF at 15 fps.
- The renderer pads images to match the desired output dimensions while preserving aspect ratio.
- **White background:** All animations maintain a bright white (`#ffffff`) background throughout, preventing dark flashes during transitions.

---

## Troubleshooting

- If MP4 export fails, ensure `ffmpeg` is installed and discoverable on your PATH.
- For very large PDFs, use the CLI to pre-trim or decrease dimensions to reduce processing requirements.
- If you see validation errors for size or page count, reduce your PDF accordingly.

---

## License

MIT