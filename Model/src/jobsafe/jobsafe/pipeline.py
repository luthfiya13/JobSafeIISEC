"""jobsafe.pipeline

A lightweight input processing pipeline that normalises various user inputs
(text strings, image files, or URLs) into clean textual content suitable for
the JOBSAFE risk assessment engines.

The pipeline is deliberately kept free of any web‑framework code – it only
produces the dictionary that the frontend can render.  It can be used by the
backend services, CLI tools, or interactive demos.
"""

from __future__ import annotations

import json
import logging
import pathlib
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)

def _load_text_from_file(file_path: Union[str, pathlib.Path]) -> str:
    """Read a plain‑text file.
    """
    p = pathlib.Path(file_path)
    if not p.is_file():
        raise FileNotFoundError(f"Input file not found: {p}")
    return p.read_text(encoding="utf-8")

def _run_ocr(image_path: Union[str, pathlib.Path]) -> str:
    """Run OCR on an image using *easyocr* if available.
    """
    try:
        import easyocr  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "easyocr is required for OCR processing but is not installed. "
            "Install it with `pip install easyocr` or use a plain text input."
        ) from exc
    reader = easyocr.Reader(["id", "en"], gpu=False)
    img = pathlib.Path(image_path)
    if not img.is_file():
        raise FileNotFoundError(f"Image file not found: {img}")
    ocr_result = reader.readtext(str(img), detail=0, paragraph=True)
    return "\n".join(ocr_result)

def _fetch_url_text(url: str) -> str:
    """Fetch a web page and extract the main textual content.
    """
    try:
        import requests  # type: ignore
        from bs4 import BeautifulSoup  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Fetching URLs requires `requests` and `beautifulsoup4`. "
            "Install them with `pip install requests beautifulsoup4`."
        ) from exc
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    texts = [t.strip() for t in soup.stripped_strings if t]
    return "\n".join(texts)

def process_input(
    raw_input: Union[str, pathlib.Path],
    *,
    mode: str = "hybrid",
    source_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Normalize user input and run the JOBSAFE engine.
    """
    if source_type not in {None, "text", "image", "url"}:
        raise ValueError("source_type must be one of None, 'text', 'image', or 'url'")

    # Determine input type
    if isinstance(raw_input, (str, pathlib.Path)) and pathlib.Path(str(raw_input)).exists():
        p = pathlib.Path(raw_input)
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif"}:
            inferred_type = "image"
        else:
            inferred_type = "text"
        content_source = p
    else:
        inferred_type = "text"
        content_source = raw_input

    if source_type:
        inferred_type = source_type

    if inferred_type == "image":
        logger.debug("Running OCR on image %s", content_source)
        raw_text = _run_ocr(content_source)  # type: ignore[arg-type]
    elif inferred_type == "url":
        logger.debug("Fetching URL %s", content_source)
        raw_text = _fetch_url_text(str(content_source))
    else:
        if isinstance(content_source, pathlib.Path):
            raw_text = _load_text_from_file(content_source)
        else:
            raw_text = str(content_source)

    from .hybrid_engine import JobsafeHybridEngine
    engine = JobsafeHybridEngine()
    result = engine.analyze(raw_text, mode=mode)
    result["_pipeline"] = {
        "source": str(content_source),
        "detected_type": inferred_type,
        "engine_mode": mode,
    }
    return result
