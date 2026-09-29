import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Any

def scrape_job_url(url: str, timeout: int = 8) -> Dict[str, Any]:
    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "id,en-US;q=0.9,en;q=0.8"
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        if response.status_code >= 400:
            return {
                "success": False,
                "error": f"Halaman tidak dapat diakses (Status: {response.status_code}). Pastikan tautan masih aktif atau salin teksnya secara manual."
            }
        
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove scripts, styles, forms, navigations
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
            tag.decompose()

        # Extract title
        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        # Extract text from main containers if possible
        main_content = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile(r"content|job|deskripsi|posting", re.I))
        if main_content:
            text = main_content.get_text(separator="\n", strip=True)
        else:
            text = soup.body.get_text(separator="\n", strip=True) if soup.body else ""

        # Normalize lines
        lines = [line.strip() for line in text.splitlines() if len(line.strip()) > 5]
        extracted_text = "\n".join(lines[:100]) # First 100 meaningful lines

        if len(extracted_text) < 30:
            return {
                "success": False,
                "error": "Teks konten dari tautan terlalu sedikit atau halaman dilindungi captcha/login. Silakan tempel teks lowongan secara manual."
            }

        return {
            "success": True,
            "title": title,
            "text": extracted_text,
            "url": url
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Koneksi ke alamat tautan memakan waktu terlalu lama (timeout). Silakan periksa kembali tautan atau tempel teks secara manual."
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": "Kami belum dapat mengakses tautan lowongan ini. Silakan salin teks lowongan secara langsung ke tab Teks."
        }
