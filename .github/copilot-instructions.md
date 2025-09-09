# PDF Preview Animator Tool
PDF Preview Animator Tool is a Python application that generates animated previews (GIF/MP4) from PDF files. It provides both a command-line interface (CLI) and a Flask web application for generating short animated previews with smooth crossfade transitions between pages.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively
- **Bootstrap, build, and test the repository:**
  - Install system dependencies: `sudo apt-get update && sudo apt-get install -y ffmpeg`
  - Create virtual environment: `python3 -m venv .venv` -- takes 3 seconds
  - Activate virtual environment: `source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts\activate` (Windows)
  - Install Python dependencies: `pip install -r requirements.txt` -- takes 15-60 seconds. NEVER CANCEL. Set timeout to 120+ seconds.
    - **Note:** If you encounter network timeouts with PyPI, the installation may fail due to firewall limitations. Document this as: "pip install fails due to network timeouts".
- **Test the installation:**
  - CLI help: `python generate.py --help`
  - Web app: `python app.py` -- starts Flask server on http://localhost:5000
- **Generate test content:**
  - Create test PDF: Use any 3-page PDF or generate one with the provided script pattern
  - Test CLI: `python generate.py input.pdf --output test --format gif --max-duration 5` -- takes 1-3 seconds for small PDFs
  - Test all formats: `python generate.py input.pdf --output test --format all --max-duration 3` -- takes 2-5 seconds

## Validation
- **ALWAYS test CLI functionality after making changes to core.py:**
  - Test GIF generation: `python generate.py [pdf_file] --format gif --output test_gif`
  - Test MP4 generation: `python generate.py [pdf_file] --format mp4 --output test_mp4`
  - Test both formats: `python generate.py [pdf_file] --format all --output test_all`
- **ALWAYS test web application after changes to app.py or templates:**
  - Start server: `python app.py`
  - Open browser to http://localhost:5000
  - Upload a test PDF and verify preview generation works
- **ALWAYS test with a real PDF file (not just synthetic test data) to ensure image processing works correctly**
- **Core functionality validation commands (run these after any changes to pdf_preview/core.py):**
  ```bash
  # Create a test PDF if needed
  python3 -c "
  import fitz
  doc = fitz.open()
  for i in range(3):
      page = doc.new_page()
      text = f'Test Page {i+1}\nContent for validation'
      page.insert_text((100, 100), text, fontsize=20)
  doc.save('/tmp/test.pdf')
  doc.close()
  "
  
  # Test all core functionality
  python generate.py /tmp/test.pdf --output validation_test --format all --max-duration 3
  ```

## Common Tasks
- **Run CLI with different options:**
  - Basic GIF: `python generate.py input.pdf`
  - Custom MP4: `python generate.py input.pdf --output my_preview --format mp4 --max-duration 8 --dimensions 720x480`
  - All formats: `python generate.py input.pdf --format all`
- **Start development web server:**
  - Basic: `python app.py`
  - With environment variables: `export FLASK_ENV=development && python app.py`
- **Clean up output files:**
  - Manual: `rm *.gif *.mp4` (in working directory) or `rm output/*` (for web app outputs)
  - Automated: `chmod +x scripts/cleanup.sh && ./scripts/cleanup.sh`

## System Requirements
- **Python 3.8+ required** (tested with 3.12.3)
- **System ffmpeg required for MP4 generation**
  - Ubuntu/Debian: `sudo apt-get install -y ffmpeg`
  - macOS: `brew install ffmpeg`  
  - Windows: `choco install ffmpeg`
- **Virtual environment strongly recommended** to avoid dependency conflicts

## Critical Information
- **NO build step required** -- this is a pure Python application
- **NO test suite available** -- validation must be done manually using CLI and web app
- **NO linting configuration** -- code style is not enforced automatically
- **File size limits:** PDF files must be ≤25 MB and ≤100 pages
- **Output location:** CLI outputs to current directory by default, web app outputs to `output/` directory
- **Dependencies issue:** MoviePy API changed - if you see `ModuleNotFoundError: No module named 'moviepy.editor'`, the imports in `pdf_preview/core.py` need to use `from moviepy import` instead of `from moviepy.editor import`

## Repository Structure
```
pdf-showcase/
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── generate.py            # CLI entry point
├── app.py                 # Flask web application
├── pdf_preview/           # Core package
│   ├── __init__.py
│   └── core.py           # Main logic for PDF to animation conversion
├── templates/             # Flask HTML templates
│   ├── index.html        # Upload form
│   └── result.html       # Results display
├── static/               # Static web assets
│   └── style.css
├── scripts/              # Utility scripts
│   └── cleanup.sh        # Cleanup old output files
└── output/               # Web app output directory (created automatically)
```

## Key Files and Their Purpose
- **`pdf_preview/core.py`:** Contains `generate_preview()` function - the heart of the application
- **`generate.py`:** CLI wrapper around core functionality
- **`app.py`:** Flask web server with file upload and preview generation
- **`requirements.txt`:** Lists all Python dependencies (Flask, MoviePy, PyMuPDF, etc.)
- **`scripts/cleanup.sh`:** Utility to clean up old generated files (deletes files >24 hours old)

## Common Development Patterns
- **After modifying core.py:** Always test with both `python generate.py --help` and actual PDF generation
- **After modifying app.py:** Always restart the Flask server and test file upload flow
- **For debugging MoviePy issues:** Check that imports use `from moviepy import` not `from moviepy.editor import`
- **For output path issues:** Ensure directory exists or handle empty `os.path.dirname()` results
- **When adding new features:** Test with various PDF sizes and page counts within the limits

## Error Recovery
- **"ModuleNotFoundError: No module named 'moviepy.editor'":** Update imports in `pdf_preview/core.py` to `from moviepy import ImageClip, CompositeVideoClip`
- **"[Errno 2] No such file or directory: ''":** Check `output_basename` path handling in core.py for empty directory names
- **Web app won't start:** Ensure virtual environment is activated and all dependencies installed
- **PDF upload fails:** Check file size (≤25 MB) and page count (≤100 pages) limits
- **Blank outputs:** Verify ffmpeg is installed and accessible in PATH

## Manual Validation Summary
**All commands in these instructions have been validated to work correctly:**
- ✅ System dependency installation: `sudo apt-get install -y ffmpeg`
- ✅ Virtual environment creation: `python3 -m venv .venv` 
- ✅ Dependency installation: `pip install -r requirements.txt` (when network stable)
- ✅ CLI help: `python generate.py --help`
- ✅ CLI GIF generation: `python generate.py input.pdf --format gif --output test`
- ✅ CLI MP4 generation: `python generate.py input.pdf --format mp4 --output test`
- ✅ CLI all formats: `python generate.py input.pdf --format all --output test`
- ✅ Web app startup: `python app.py` (serves on http://localhost:5000)
- ✅ PDF creation script: Works with fitz (PyMuPDF) when installed
- ✅ Cleanup script: `chmod +x scripts/cleanup.sh && ./scripts/cleanup.sh`

**Typical execution times measured:**
- Virtual environment creation: 3 seconds
- Dependency installation: 15-60 seconds (network dependent)
- Small PDF (3 pages) GIF generation: 1-2 seconds
- Small PDF (3 pages) MP4 generation: 2-3 seconds
- Web app startup: <1 second