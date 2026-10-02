import io
import re
from typing import Dict, Any

import cv2
import numpy as np
from PIL import Image


def _clean_ocr_text(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    cleaned = cleaned.replace("\u00a0", " ")
    cleaned = re.sub(r"(?<!\w)\s+(?=\W)", " ", cleaned)
    return cleaned.strip()


def extract_text_from_image(image_bytes: bytes) -> Dict[str, Any]:
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        width, height = image.size

        if width == 0 or height == 0:
            return {
                "success": False,
                "error": "Format berkas gambar tidak valid atau rusak. Harap unggah berkas PNG, JPG, atau JPEG."
            }

        # Improve OCR accuracy on screenshots by enlarging and thresholding for high contrast text.
        rgb = np.array(image)
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        gray = cv2.bilateralFilter(gray, 3, 25, 25)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)

        try:
            from rapidocr_onnxruntime import RapidOCR
            detector = RapidOCR()
            results, _ = detector(processed)

            if results:
                extracted_lines = []
                for item in results:
                    if not item or len(item) < 2:
                        continue
                    text = str(item[1]).strip()
                    if text:
                        extracted_lines.append(text)

                cleaned_text = _clean_ocr_text("\n".join(extracted_lines))
                if len(cleaned_text) >= 15:
                    return {
                        "success": True,
                        "text": cleaned_text,
                        "info": f"Ukuran gambar: {width}x{height}px | OCR akurat via RapidOCR"
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
