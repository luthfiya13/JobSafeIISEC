import io
import os
from typing import Dict, Any
from PIL import Image

def extract_text_from_image(image_bytes: bytes) -> Dict[str, Any]:
    try:
        image = Image.open(io.BytesIO(image_bytes))
        width, height = image.size

        # Try to run pytesseract if installed
        try:
            import pytesseract
            # Check if tesseract binary exists in standard windows paths if not found
            win_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe")
            ]
            for p in win_paths:
                if os.path.exists(p):
                    pytesseract.pytesseract.tesseract_cmd = p
                    break

            text = pytesseract.image_to_string(image, lang="ind+eng")
            cleaned_text = text.strip()
            if len(cleaned_text) >= 15:
                return {
                    "success": True,
                    "text": cleaned_text,
                    "info": f"Ukuran gambar: {width}x{height}px"
                }
        except Exception:
            pass

        # If OCR library is not available or extracted text is empty
        return {
            "success": False,
            "error": "Teks dalam foto belum dapat dibaca secara optimal oleh mesin OCR. Silakan pastikan gambar tajam atau salin teks ke tab Teks untuk hasil analisis terbaik."
        }

    except Exception as e:
        return {
            "success": False,
            "error": "Format berkas gambar tidak valid atau rusak. Harap unggah berkas PNG, JPG, atau JPEG."
        }
