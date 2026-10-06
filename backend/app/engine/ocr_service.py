import io
import re
from typing import Dict, Any

import cv2
import numpy as np
from PIL import Image, ImageOps


def _clean_ocr_text(text: str) -> str:
    text = (text or "").replace("\u00a0", " ").replace("\r", "\n")
    lines = [re.sub(r"[\t\f\v ]+", " ", line).strip() for line in text.split("\n")]
    lines = [line for line in lines if line]
    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\s+([,.;:!?%])", r"\1", cleaned)
    return cleaned.strip()


def _ordered_text(results) -> tuple[str, float]:
    items = []
    heights = []
    for item in results or []:
        if not item or len(item) < 2:
            continue
        text = str(item[1]).strip()
        if not text:
            continue
        points = np.asarray(item[0], dtype=np.float32)
        y_top = float(np.min(points[:, 1])) if points.ndim == 2 and points.shape[1] >= 2 else 0.0
        y_bottom = float(np.max(points[:, 1])) if points.ndim == 2 and points.shape[1] >= 2 else y_top + 20
        x_left = float(np.min(points[:, 0])) if points.ndim == 2 and points.shape[1] >= 2 else 0.0
        height = max(1.0, y_bottom - y_top)
        confidence = float(item[2]) if len(item) > 2 else 50.0
        items.append({"text": text, "y": (y_top + y_bottom) / 2, "x": x_left, "height": height, "confidence": confidence})
        heights.append(height)

    if not items:
        return "", 0.0

    line_tolerance = max(12.0, float(np.median(heights)) * 0.65)
    lines = []
    for item in sorted(items, key=lambda entry: (entry["y"], entry["x"])):
        if not lines or abs(item["y"] - lines[-1]["center"]) > line_tolerance:
            lines.append({"center": item["y"], "items": [item]})
        else:
            lines[-1]["items"].append(item)
            lines[-1]["center"] = sum(entry["y"] for entry in lines[-1]["items"]) / len(lines[-1]["items"])

    text = "\n".join(
        " ".join(entry["text"] for entry in sorted(line["items"], key=lambda item: item["x"]))
        for line in lines
    )
    confidence = sum(item["confidence"] for item in items) / len(items)
    return _clean_ocr_text(text), confidence


def extract_text_from_image(image_bytes: bytes) -> Dict[str, Any]:
    try:
        image = ImageOps.exif_transpose(Image.open(io.BytesIO(image_bytes))).convert("RGB")
        width, height = image.size

        if width == 0 or height == 0:
            return {
                "success": False,
                "error": "Format berkas gambar tidak valid atau rusak. Harap unggah berkas PNG, JPG, atau JPEG."
            }

        # Keep enough detail for small text, while bounding inference memory for phone photos.
        rgb = np.array(image)
        height, width = rgb.shape[:2]
        longest_side = max(width, height)
        scale = min(4.0, max(2400.0, min(4600.0, float(longest_side))) / longest_side)
        scale = min(scale, (8_000_000 / (width * height)) ** 0.5)
        if abs(scale - 1.0) > 0.01:
            rgb = cv2.resize(rgb, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC if scale > 1 else cv2.INTER_AREA)

        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        # Remove sensor noise, then improve local contrast for text over shadows or colored backgrounds.
        denoised = cv2.bilateralFilter(gray, 5, 35, 35)
        clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8)).apply(denoised)
        adaptive = cv2.adaptiveThreshold(
            clahe, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, 11
        )
        _, otsu = cv2.threshold(clahe, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        variants = [
            rgb,
            cv2.cvtColor(clahe, cv2.COLOR_GRAY2RGB),
            cv2.cvtColor(adaptive, cv2.COLOR_GRAY2RGB),
            cv2.cvtColor(otsu, cv2.COLOR_GRAY2RGB),
        ]

        try:
            from rapidocr_onnxruntime import RapidOCR
            detector = RapidOCR()
            candidates = []
            for variant in variants:
                results, _ = detector(variant)
                text, confidence = _ordered_text(results)
                if len(text) >= 15:
                    quality = confidence * 0.8 + min(len(text), 1800) * 0.02
                    candidates.append((quality, text))

            if candidates:
                _, cleaned_text = max(candidates, key=lambda candidate: candidate[0])
                return {
                    "success": True,
                    "text": cleaned_text,
                    "info": f"Ukuran gambar: {width}x{height}px | RapidOCR memilih hasil dengan keterbacaan terbaik"
                }
        except Exception:
            pass

        return {
            "success": False,
            "error": "Teks dalam foto belum dapat dibaca secara optimal oleh mesin OCR. Pastikan gambar jelas, scan tidak terlalu kecil, atau salin teks lowongan ke tab Teks untuk hasil analisis terbaik."
        }

    except Exception:
        return {
            "success": False,
            "error": "Format berkas gambar tidak valid atau rusak. Harap unggah berkas PNG, JPG, atau JPEG."
        }
