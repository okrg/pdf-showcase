import os
import math
import uuid
from typing import List, Tuple, Literal, Optional

import numpy as np
import fitz  # PyMuPDF
from moviepy import ImageClip, CompositeVideoClip
import moviepy


class PDFValidationError(ValueError):
    pass


def _parse_dimensions(dimensions: str) -> Tuple[int, int]:
    try:
        w_str, h_str = dimensions.lower().split("x")
        w, h = int(w_str), int(h_str)
        if w <= 0 or h <= 0:
            raise ValueError
        return w, h
    except Exception:
        raise ValueError('Invalid dimensions. Expected format "WIDTHxHEIGHT", e.g., "480x640".')


def _validate_pdf(pdf_path: str, max_size_bytes: int = 25 * 1024 * 1024, max_pages: int = 100) -> None:
    if not os.path.isfile(pdf_path):
        raise PDFValidationError("Input file does not exist.")
    if not pdf_path.lower().endswith(".pdf"):
        raise PDFValidationError("Input file must be a PDF (.pdf).")

    size = os.path.getsize(pdf_path)
    if size > max_size_bytes:
        raise PDFValidationError("PDF exceeds the 25 MB size limit.")

    try:
        with fitz.open(pdf_path) as doc:
            page_count = doc.page_count
    except Exception:
        raise PDFValidationError("Failed to open PDF. The file may be corrupted or not a valid PDF.")

    if page_count > max_pages:
        raise PDFValidationError(f"PDF exceeds the maximum page count of {max_pages} (found {page_count}).")


def _select_pages(total_pages: int, max_duration: float, min_per_page: float, crossfade: float) -> List[int]:
    # Find the maximum number of pages we can show within max_duration given min_per_page and crossfade
    # Total duration approx: n * per_page - (n - 1) * crossfade
    # We must keep per_page >= min_per_page, so try increasing n until duration exceeds max_duration
    n = 1
    while True:
        duration = n * min_per_page - (n - 1) * crossfade
        if duration > max_duration:
            n -= 1
            break
        n += 1
        if n > total_pages:
            n = total_pages
            break
    n = max(1, n)

    if total_pages <= n:
        return list(range(total_pages))

    # Sample evenly, ensuring we include first and last
    indices = [0]
    if n > 2:
        # Evenly space n-2 indices between 1 and total_pages-2 inclusive
        step = (total_pages - 1) / (n - 1)
        for i in range(1, n - 1):
            idx = round(i * step)
            indices.append(idx)
    indices.append(total_pages - 1)
    # Deduplicate and sort
    indices = sorted(set(indices))
    # If deduplication reduced count, fill in as best as possible
    while len(indices) < n:
        for k in range(total_pages):
            if k not in indices:
                indices.append(k)
            if len(indices) == n:
                break
    return sorted(indices)


def _render_page_to_array(page: fitz.Page, target_w: int, target_h: int) -> np.ndarray:
    # Compute scale so the longer side fits within target while preserving aspect ratio
    rect = page.rect
    page_w, page_h = rect.width, rect.height
    scale = min(target_w / page_w, target_h / page_h)
    # Avoid zero scale for tiny target sizes
    scale = max(scale, 0.1)

    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), colorspace=fitz.csRGB, alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)

    # Letterbox/pad to exact dimensions on white background
    canvas = np.full((target_h, target_w, 3), 255, dtype=np.uint8)
    y_off = (target_h - img.shape[0]) // 2
    x_off = (target_w - img.shape[1]) // 2
    canvas[y_off:y_off + img.shape[0], x_off:x_off + img.shape[1]] = img
    return canvas


def _compute_per_page_duration(n_pages: int, max_duration: float, min_per_page: float, crossfade: float) -> float:
    # total = n * d - (n - 1) * crossfade <= max_duration
    # => d <= (max_duration + (n - 1) * crossfade) / n
    upper = (max_duration + (n_pages - 1) * crossfade) / n_pages
    return max(min_per_page, upper)


def generate_preview(
    pdf_path: str,
    output_basename: str,
    max_duration: float = 10.0,
    format: Literal["gif", "mp4", "all"] = "gif",
    dimensions: str = "480x640",
    crossfade: float = 0.15,
    fps_gif: int = 15,
    fps_mp4: int = 24,
) -> List[str]:
    """
    Convert a PDF into an animated preview (GIF/MP4) with crossfades.

    Args:
        pdf_path: Path to the input PDF.
        output_basename: Base path (without extension) for output files.
        max_duration: Maximum duration in seconds for the animation.
        format: "gif", "mp4", or "all".
        dimensions: "WIDTHxHEIGHT" string, e.g., "480x640".
        crossfade: Crossfade duration between pages in seconds (0.1 to 0.2 suggested).
        fps_gif: Frame rate for GIF output.
        fps_mp4: Frame rate for MP4 output.

    Returns:
        List of generated file paths.

    Raises:
        PDFValidationError for validation failures.
        ValueError for parameter issues.
    """
    if max_duration <= 0:
        raise ValueError("max_duration must be positive.")
    if crossfade < 0 or crossfade >= 1.0:
        raise ValueError("crossfade must be between 0 and 1 second for best results.")
    target_w, target_h = _parse_dimensions(dimensions)

    _validate_pdf(pdf_path)

    outputs: List[str] = []
    min_per_page = 0.4

    with fitz.open(pdf_path) as doc:
        total_pages = doc.page_count
        indices = _select_pages(total_pages, max_duration, min_per_page, crossfade)

        per_page = _compute_per_page_duration(len(indices), max_duration, min_per_page, crossfade)

        # Render images
        frames: List[np.ndarray] = []
        for idx in indices:
            page = doc.load_page(idx)
            frames.append(_render_page_to_array(page, target_w, target_h))

    # Build ImageClips with durations
    clips: List[ImageClip] = []
    for i, frame in enumerate(frames):
        clip = ImageClip(frame).with_duration(per_page)
        if i > 0 and crossfade > 0:
            # We'll apply crossfade-in via CompositeVideoClip start times later
            pass
        clips.append(clip)

    # Crossfade via CompositeVideoClip with overlapping starts
    if len(clips) == 1 or crossfade <= 0:
        final = CompositeVideoClip([clips[0].with_start(0)], size=(target_w, target_h)).with_duration(per_page)
    else:
        placed = []
        for i, c in enumerate(clips):
            start = i * (per_page - crossfade)
            if i > 0:
                c = c.with_start(start).with_effects([moviepy.vfx.FadeIn(crossfade)])
            else:
                c = c.with_start(start)
            placed.append(c)
        total_duration = (len(clips) - 1) * (per_page - crossfade) + per_page
        final = CompositeVideoClip(placed, size=(target_w, target_h)).with_duration(total_duration)

    # Write outputs
    output_dir = os.path.dirname(output_basename)
    if output_dir:  # Only create directory if there's a directory component
        os.makedirs(output_dir, exist_ok=True)
    fmt = format.lower()
    if fmt not in {"gif", "mp4", "all"}:
        raise ValueError('format must be one of: "gif", "mp4", "all".')

    if fmt in {"gif", "all"}:
        gif_path = f"{output_basename}.gif"
        final.write_gif(gif_path, fps=fps_gif)
        outputs.append(gif_path)

    if fmt in {"mp4", "all"}:
        mp4_path = f"{output_basename}.mp4"
        final.write_videofile(mp4_path, codec="libx264", audio=False, fps=fps_mp4)
        outputs.append(mp4_path)

    final.close()
    for c in clips:
        c.close()

    return outputs