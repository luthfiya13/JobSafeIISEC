#!/usr/bin/env python3
"""
=============================================================================
JOBSAFE - Alat Uji Coba Multi-Input (Teks, Foto/Poster, dan Link/URL)
=============================================================================
File ini dibuat untuk mempermudah Anda menguji coba model JOBSAFE secara mandiri.
Dapat dihapus atau diabaikan setelah pengujian selesai.

Cara Menjalankan:
    python uji_coba_model.py
=============================================================================
"""

import os
import sys
import re
import urllib.request
from pathlib import Path
from typing import Optional, Tuple

# Reconfigure stdout for UTF-8 on Windows
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from jobsafe import JobsafeHybridEngine

# Inisialisasi engine JOBSAFE
engine = JobsafeHybridEngine()

def extract_text_from_url(url: str) -> Tuple[str, Optional[str]]:
    """Mengambil dan mengekstrak teks isi dari halaman web / tautan."""
    clean_url = url.strip()
    if not clean_url.startswith(("http://", "https://")):
        clean_url = "https://" + clean_url
        
    print(f"\n[+] Menghubungi URL: {clean_url} ...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        req = urllib.request.Request(clean_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8", errors="ignore")
            # Hapus tag script dan style
            cleaned_html = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.DOTALL | re.IGNORECASE)
            # Ambil teks bersih dari tag HTML
            text = re.sub(r"<[^>]+>", " ", cleaned_html)
            text = re.sub(r"\s+", " ", text).strip()
            print(f"[OK] Berhasil mengekstrak {len(text)} karakter dari halaman web.")
            return text[:10000], clean_url
    except Exception as e:
        print(f"[!] Catatan: Tidak dapat mengunduh konten teks dari web ({e}).")
        print(f"[*] Engine akan menganalisis domain URL tersebut secara langsung.")
        return f"Pendaftaran lowongan kerja melalui link: {clean_url}", clean_url

def extract_text_from_image(image_path_str: str) -> str:
    """Mengekstrak teks dari file gambar (poster / flyer) menggunakan OCR."""
    img_path = Path(image_path_str.strip().strip('"').strip("'"))
    if not img_path.exists():
        print(f"[!] File gambar tidak ditemukan di path: {img_path}")
        return ""
        
    print(f"\n[+] Membaca file gambar: {img_path.name} ...")
    
    # 1. Coba pytesseract jika tersedia
    try:
        from PIL import Image
        import pytesseract
        
        img = Image.open(img_path)
        print("[+] Menjalankan OCR pada gambar...")
        ocr_text = pytesseract.image_to_string(img, lang="ind+eng")
        if ocr_text.strip():
            print(f"[OK] OCR Berhasil ({len(ocr_text)} karakter terdeteksi).")
            return ocr_text.strip()
    except Exception as e:
        pass

    # 2. Coba easyocr jika tersedia
    try:
        import easyocr
        reader = easyocr.Reader(['id', 'en'], gpu=False)
        results = reader.readtext(str(img_path), detail=0)
        ocr_text = " ".join(results).strip()
        if ocr_text:
            print(f"[OK] EasyOCR Berhasil ({len(ocr_text)} karakter terdeteksi).")
            return ocr_text
    except Exception as e:
        pass

    # Fallback jika binary Tesseract lokal belum ada di PATH
    print("\n[!] Binary Tesseract/EasyOCR belum terdeteksi otomatis pada sistem ini.")
    print("    Silakan masukkan/ketik teks yang tertera pada poster secara manual di bawah ini:")
    manual_input = input(">> Teks poster: ").strip()
    return manual_input

def tampilkan_hasil_analisis(hasil: dict, url_ref: Optional[str] = None):
    """Menampilkan hasil analisis model dengan format visual yang jelas dan informatif."""
    level = hasil["risk_level"]
    score = hasil["risk_score"]
    
    badge = "[HIGH - RISIKO TINGGI]" if level == "HIGH" else ("[MEDIUM - RISIKO SEDANG]" if level == "MEDIUM" else ("[LOW - RISIKO RENDAH]" if level == "LOW" else "[INSUFFICIENT_INPUT]"))
    
    print("\n" + "=" * 70)
    print("               HASIL PENILAIAN RISIKO JOBSAFE MODEL")
    print("=" * 70)
    print(f" Tingkat Risiko       : {badge}")
    print(f" Skor Risiko          : {score} / 100")
    print(f" Mode Analisis        : {hasil['meta'].get('hybrid_mode', 'hybrid').upper()}")
    print(f" Keputusan Model      : {hasil['meta'].get('hybrid_decision_type', 'NORMAL_EVALUATION')}")
    print("-" * 70)
    
    # Verifikasi Entitas
    verif = hasil.get("verification_status", {})
    status_verif = verif.get("status", "UNVERIFIED")
    icon_verif = "[VERIFIED]" if status_verif == "VERIFIED" else ("[CONTRADICTORY]" if status_verif == "CONTRADICTORY" else "[UNVERIFIED]")
    print(f"\n[1] STATUS VERIFIKASI ENTITAS & KANAL:")
    print(f"    Status   : {icon_verif} {status_verif}")
    print(f"    Catatan  : {verif.get('details', '-')}")
    if verif.get("claimed_employer"):
        print(f"    Instansi : {', '.join(verif['claimed_employer'])}")
    
    # Indikator Risiko R1 - R10 yang Ditemukan
    inds = hasil.get("detected_indicators", [])
    print(f"\n[2] INDIKATOR RISIKO TERDETEKSI ({len(inds)} Indikator):")
    if not inds:
        print("    [OK] Tidak ditemukan pola risiko mencurigakan pada input ini.")
    else:
        for i in inds:
            kekuatan = "KUAT (STRONG)" if i["strength"] == "STRONG" else ("SEDANG (MODERATE)" if i["strength"] == "MODERATE" else "LEMAH (WEAK)")
            print(f"\n    * [{i['code']}] {i['name']}")
            print(f"      - Tingkat Bahaya : {kekuatan} (Confidence: {i['confidence']})")
            print(f"      - Potongan Bukti : \"{i['evidence']}\"")
            print(f"      - Alasan Sistem  : {i['reason']}")
            if i.get("legal_basis") and i["legal_basis"] != "-":
                print(f"      - Landasan Hukum : {i['legal_basis']}")
            if i.get("syariah_basis"):
                print(f"      - Maqasid Syariah: {i['syariah_basis']}")

    # Skor 5 Dimensi Risiko
    print(f"\n[3] SKOR 5 DIMENSI RISIKO:")
    dims = hasil.get("dimension_scores", {})
    print(f"    * Finansial (R1, R2, R6)           : {dims.get('financial', 0)}%")
    print(f"    * Data & Identitas (R3)            : {dims.get('data_identity', 0)}%")
    print(f"    * Keabsahan & Deception (R4, R5, R8): {dims.get('legitimacy_deception', 0)}%")
    print(f"    * Eksploitasi & Keselamatan (R7, R9): {dims.get('exploitation_safety', 0)}%")
    print(f"    * Manipulasi Psikologis (R10)      : {dims.get('manipulation', 0)}%")

    # Penjelasan & Rekomendasi
    print(f"\n[4] PENJELASAN & REKOMENDASI TINDAKAN:")
    print(f"    Penjelasan Sistem:")
    print(f"    \"{hasil.get('risk_explanation', hasil.get('message', ''))}\"")
    print(f"\n    Panduan untuk Pelamar:")
    for r in hasil.get("recommended_actions", []):
        print(f"    - {r}")

    # Checklist Tabayyun
    print(f"\n[5] CHECKLIST VERIFIKASI MANDIRI (TABAYYUN):")
    for c in hasil.get("verification_checklist", []):
        print(f"    [ ] {c}")

    print("\n" + "-" * 70)
    print(f" Disclaimer: {hasil.get('disclaimer', '')}")
    print("=" * 70 + "\n")

def menu_utama():
    while True:
        print("\n" + "=" * 65)
        print("         SELAMAT DATANG DI PENGUJIAN MODEL JOBSAFE")
        print("=" * 65)
        print(" Pilih metode input lowongan kerja yang ingin Anda uji:")
        print("  [1] Input Teks (Ketik / Tempel Teks Lowongan Bebas)")
        print("  [2] Input Link / URL Web Lowongan")
        print("  [3] Input Foto / Poster Lowongan Kerja (File Gambar)")
        print("  [4] Uji Coba Contoh Kasus Preset (Scam Biaya / Task / BUMN / UMKM)")
        print("  [0] Keluar")
        print("=" * 65)
        
        pilihan = input("Pilih menu [1-4 atau 0]: ").strip()
        
        if pilihan in ("0", "exit", "keluar", "q"):
            print("\nTerima kasih. Pengujian selesai.")
            break
            
        elif pilihan == "1":
            print("\n" + "-" * 60)
            print("INPUT TEKS: Ketik atau tempel teks lowongan kerja.")
            print("(Tekan ENTER 2 kali jika teks Anda selesai)")
            print("-" * 60)
            lines = []
            while True:
                line = input()
                if not line and lines and not lines[-1]:
                    break
                lines.append(line)
            teks = "\n".join(lines).strip()
            if not teks:
                print("[!] Teks tidak boleh kosong.")
                continue
            hasil = engine.analyze(teks, mode="hybrid")
            tampilkan_hasil_analisis(hasil)
            
        elif pilihan == "2":
            print("\n" + "-" * 60)
            url = input("Masukkan Link / URL Lowongan: ").strip()
            if not url:
                print("[!] URL tidak boleh kosong.")
                continue
            teks_web, clean_url = extract_text_from_url(url)
            hasil = engine.analyze(teks_web, url=clean_url, mode="hybrid")
            tampilkan_hasil_analisis(hasil, url_ref=clean_url)
            
        elif pilihan == "3":
            print("\n" + "-" * 60)
            print("INPUT FOTO: Masukkan path file gambar poster.")
            print("Contoh: poster_loker.jpg atau C:\\Users\\User\\Pictures\\loker.png")
            print("-" * 60)
            path_gambar = input("Path file gambar: ").strip()
            if not path_gambar:
                print("[!] Path gambar tidak boleh kosong.")
                continue
            teks_ocr = extract_text_from_image(path_gambar)
            if not teks_ocr:
                print("[!] Tidak ada teks yang dapat diproses.")
                continue
            print(f"\n[Teks yang diekstrak dari gambar]:\n\"{teks_ocr}\"")
            hasil = engine.analyze(teks_ocr, mode="hybrid")
            tampilkan_hasil_analisis(hasil)
            
        elif pilihan == "4":
            contoh = [
                ("1. Penipuan Uang Muka / Seragam (Scam Fee)", 
                 "LOWONGAN BUMN PT Maju Jaya. Dibutuhkan 20 staff admin, gaji 8 juta. Wajib transfer biaya pendaftaran Rp 250.000 untuk seragam. Hubungi WA 081234567890. Kuota terbatas!"),
                ("2. Penipuan Tugas Like & Subscribe / Top-Up (Task Scam)",
                 "Kerja sampingan dari rumah, tugas harian like & subscribe, komisi Rp 50.000 per tugas. Wajib top up saldo awal 500rb, modal akan dikembalikan beserta komisi. Pasti profit."),
                ("3. Pencatutan BUMN & Domain Palsu (Impersonation)",
                 "LOWONGAN BUMN PT Pertamina 2026 admin teller. Daftar di goletskerja.com atau scan QR. Kirim foto KTP dan nomor rekening sekarang juga."),
                ("4. Penipuan Kerja Luar Negeri / CS Kamboja (TPPO / Scam Hubs)",
                 "Loker Kamboja customer service online gaji $2000 tanpa pengalaman tanpa bahasa Inggris. Proses cepat jalur khusus tanpa visa kerja, biaya keberangkatan potong gaji."),
                ("5. Lowongan UMKM Sah dengan Kontak WA (Legitimate UMKM)",
                 "Toko Kue Armindo Magelang butuh kasir toko. Jl. Soekarno Hatta No.2. Syarat: min SMA, jujur, pengalaman 1 tahun. Kirim lamaran ke armindomagelang21@gmail.com atau WA 082227187988. Gaji sesuai UMK. Tidak dipungut biaya apa pun.")
            ]
            print("\nPILIH CONTOH KASUS:")
            for idx, (judul, _) in enumerate(contoh, 1):
                print(f" [{idx}] {judul}")
            p_kasus = input("\nPilih nomor contoh [1-5]: ").strip()
            if p_kasus in ("1", "2", "3", "4", "5"):
                judul_pilih, teks_pilih = contoh[int(p_kasus) - 1]
                print(f"\n[Menguji Contoh]: {judul_pilih}")
                print(f"Teks:\n\"{teks_pilih}\"")
                hasil = engine.analyze(teks_pilih, mode="hybrid")
                tampilkan_hasil_analisis(hasil)
            else:
                print("[!] Pilihan tidak valid.")

if __name__ == "__main__":
    menu_utama()
