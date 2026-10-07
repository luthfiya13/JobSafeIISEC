#!/usr/bin/env python3
"""
=============================================================================
JOBSAFE MODEL QUALITY CHECK & COMPREHENSIVE STRESS-TESTING SUITE
=============================================================================
Suite ini menguji ketahanan dan akurasi model JOBSAFE terhadap berbagai skenario:
1. OCR Extracted Text (Noise, typo OCR, All Caps, spasi berantakan, poster singkat)
2. Web Scraped Text & URL (Navigasi web, HTML artifacts, shortlink, domain resmi vs phishing)
3. Direct Text / Chat (Scam R1-R10, Multi-vector scam, UMKM sah, BUMN sah)
4. Robustness & Edge Cases (Karakter aneh, teks 50k karakter, disclaimer resmi, emoji)
5. Web API Schema & Output Contract Completeness
=============================================================================
"""

import sys
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from jobsafe.hybrid_engine import JobsafeHybridEngine
from jobsafe.engine import JobsafeEngine

def run_quality_check():
    print("=" * 75)
    print("      JOBSAFE MODEL QUALITY CHECK & STRESS TEST REPORT")
    print("=" * 75)
    
    engine = JobsafeHybridEngine()
    total_tests = 0
    passed_tests = 0
    test_categories = {}

    def test_case(category: str, name: str, text: str, expected_level: str, url: str = None, check_fn=None):
        nonlocal total_tests, passed_tests
        total_tests += 1
        test_categories.setdefault(category, {"total": 0, "passed": 0})
        test_categories[category]["total"] += 1
        
        try:
            start_t = time.perf_counter()
            res = engine.analyze(text, url=url, mode="hybrid")
            dur_ms = (time.perf_counter() - start_t) * 1000
            
            level_ok = (res["risk_level"] == expected_level)
            extra_ok = True
            extra_msg = ""
            if check_fn:
                res_check = check_fn(res)
                if isinstance(res_check, tuple):
                    extra_ok, extra_msg = res_check
                else:
                    extra_ok = bool(res_check)
                
            is_pass = level_ok and extra_ok
            if is_pass:
                passed_tests += 1
                test_categories[category]["passed"] += 1
                status = "[PASS]"
            else:
                status = "[FAIL]"
                
            print(f"{status} | {category} -> {name}")
            print(f"       Expected: {expected_level} | Got: {res['risk_level']} (Score: {res['risk_score']}) | Time: {dur_ms:.2f}ms")
            if not is_pass:
                if not level_ok:
                    print(f"       [!] Level Mismatch! Expected {expected_level}, got {res['risk_level']}")
                if not extra_ok:
                    print(f"       [!] Extra Check Failed: {extra_msg}")
                print(f"       Indicators: {[i['code'] for i in res.get('detected_indicators', [])]}")
                print(f"       Floors: {res.get('meta', {}).get('floors_applied', [])}")
            return is_pass
        except Exception as e:
            print(f"[ERROR] | {category} -> {name}: Exception raised: {e}")
            return False

    print("\n--- [KATEGORI 1: SKENARIO HASIL EKSTRAKSI GAMBAR (OCR NOISE & TYPO)] ---")
    
    # 1.1 Poster Loker Scam Biaya dengan Typo OCR (0 diganti O, huruf besar kecil berantakan)
    test_case(
        "OCR Noise",
        "Poster Scam Biaya dengan Noise OCR & Line Break Acak",
        "L0W0NGAN KERJA PT MAJU J4YA\n\nPosisi: St4ff Adm1n\nSyarat: Min SMA\nW4jib tr4nsfer bi4ya pendaftaran Rp 250.000,- untuk s3ragam ke rek BCA 12345678.\nHubung1 WA 081234567890",
        "HIGH",
        check_fn=lambda r: ("R1" in [i["code"] for i in r["detected_indicators"]], "Harus mendeteksi R1")
    )
    
    # 1.2 Poster Loker All-Caps Pencatutan BUMN + Email Gratisan (Peringatan Impersonasi)
    test_case(
        "OCR Noise",
        "Poster All-Caps Pencatutan BUMN + Email Gratisan (Impersonation Only)",
        "REKRUTMEN BERSAMA BUMN 2026 PT PERTAMINA PERSERO DIBUKA PENDAFTARAN POSISI OPERATOR DAN ADMIN GAJI 9 JUTA KIRIM BERKAS KE EMAIL: REKRUTMEN.PERTAMINA2026@GMAIL.COM ATAU WA 081299887766",
        "MEDIUM",
        check_fn=lambda r: (r["verification_status"]["status"] == "CONTRADICTORY", "Status verifikasi harus CONTRADICTORY karena email gmail")
    )

    # 1.2b Poster Pencatutan BUMN + Penarikan Data Sensitif (Impersonation + Data Harvest)
    test_case(
        "OCR Noise",
        "Poster Pencatutan BUMN + Permintaan Foto KTP & Buku Tabungan",
        "LOKER BUMN 2026 PT PLN PERSERO. Segera daftar staf logistik. Wajib kirim foto e-KTP dan foto buku tabungan via WhatsApp 081299887766 sebelum interview.",
        "HIGH",
        check_fn=lambda r: any(i["code"] == "R3" for i in r["detected_indicators"])
    )
    
    # 1.3 Poster Loker Sah UMKM dengan OCR Berantakan
    test_case(
        "OCR Noise",
        "Poster UMKM Sah (Warung Bakso) dengan Kontak WA",
        "DIBUTUHKAN SEGERA\nKaryawan Warung Bakso Mas Joko\nAlamat: Jl. Pemuda No. 14 Semarang\nSyarat: Rajin, jujur, usia 18-30 thn.\nGaji 2,5 jt / bulan + uang makan.\nKirim biodata lewat WA: 081325001122.\nGRATIS, TIDAK DIPUNGUT BIAYA APAPUN.",
        "LOW",
        check_fn=lambda r: (r["risk_score"] < 25, "UMKM sah harus berisiko rendah")
    )

    # 1.4 Poster Terpotong / Sangat Sedikit Teks (Input Kurang Memadai)
    test_case(
        "OCR Noise",
        "Poster Singkat / Terpotong (Input Kurang Memadai)",
        "WE ARE HIRING!\nGRAPHIC DESIGNER\nApply Now!",
        "INSUFFICIENT_INPUT"
    )

    print("\n--- [KATEGORI 2: SKENARIO HASIL EKSTRAKSI LINK / WEB SCRAPING] ---")
    
    # 2.1 Scraping Web Phishing Mengatasnamakan BUMN + Minta Data Rekening
    test_case(
        "Web Scraping",
        "Web Phishing Mengatasnamakan PLN di Domain Phishing + Data Rekening",
        "PT PLN (Persero) Membuka Lowongan Kerja 2026. Silakan daftar dan input nomor rekening serta foto KTP Anda pada tautan pendaftaran berikut.",
        "HIGH",
        url="https://rekrutmen-pln-terbaru2026.xyz/daftar",
        check_fn=lambda r: (r["verification_status"]["status"] == "CONTRADICTORY", "Domain .xyz untuk PLN harus CONTRADICTORY")
    )

    # 2.1b Web Mengatasnamakan BUMN di Domain Pihak Ketiga Tanpa Kejahatan Eksplisit
    test_case(
        "Web Scraping",
        "Web Pihak Ketiga Mencatut BNI Tanpa Pungutan (Peringatan Domain)",
        "Rekrutmen BNI Bina BNI Teller 2026. Daftar di goletskerja.com. Syarat S1 semua jurusan, lokasi seluruh Indonesia.",
        "MEDIUM",
        url="https://goletskerja.com/bni-teller-2026",
        check_fn=lambda r: (r["verification_status"]["status"] == "CONTRADICTORY", "Domain goletskerja untuk BNI harus CONTRADICTORY")
    )

    # 2.2 Scraping Web Resmi Portal BUMN (FHCI BUMN)
    test_case(
        "Web Scraping",
        "Web Resmi Rekrutmen Bersama BUMN di fhcibumn.id",
        "Forum Human Capital Indonesia (FHCI) kembali menyelenggarakan Rekrutmen Bersama BUMN 2026. Tersedia lebih dari 1000 posisi di berbagai perusahaan BUMN di seluruh Indonesia. Proses seleksi gratis dan transparan.",
        "LOW",
        url="https://rekrutmenbersama2026.fhcibumn.id",
        check_fn=lambda r: (r["verification_status"]["status"] == "VERIFIED", "Domain fhcibumn.id harus VERIFIED")
    )

    # 2.3 Scraping Web Loker dengan HTML Noise & Footer Navigasi
    test_case(
        "Web Scraping",
        "Teks Hasil Scraping Penuh Header Navigasi & Copyright Footer",
        "Home | About Us | Contact | Careers | Privacy Policy | Terms of Service\nPT Mandiri Sekuritas membuka lowongan Equity Research Analyst. Penempatan: Jakarta Selatan. Kualifikasi: S1 Ekonomi/Keuangan, pengalaman 2 tahun, CFA level 1 diutamakan. Gaji kompetitif + asuransi kesehatan. Lamar sekarang melalui situs resmi https://mandirisekuritas.co.id/careers. Copyright 2026 All Rights Reserved.",
        "LOW",
        check_fn=lambda r: (r["verification_status"]["status"] == "VERIFIED" and r["risk_score"] < 25, "Mandiri Sekuritas resmi harus LOW dan VERIFIED")
    )

    # 2.4 Scraping Link Tugas Berbayar (Task Scam / Phishing Linktree)
    test_case(
        "Web Scraping",
        "Teks Web Landing Page Task Scam (Freelance Like/Follow)",
        "Program Kerja Paruh Waktu Resmi E-Commerce 2026. Dapatkan penghasilan 300rb - 1jt per hari hanya dengan like produk dan follow akun. Tugas mudah dari rumah. Masukkan nomor WhatsApp Anda untuk aktivasi akun dan terima saldo bonus deposit pertama 50rb. Hubungi manajer kami.",
        "HIGH",
        url="https://linktr.ee/freelance_online_task2026",
        check_fn=lambda r: ("R6" in [i["code"] for i in r["detected_indicators"]], "Harus mendeteksi indikator R6")
    )

    print("\n--- [KATEGORI 3: VARIASI DETEKSI MODUS PENIPUAN (R1 - R10)] ---")
    
    # 3.1 R1 - Biaya Administrasi & Seragam
    test_case(
        "Scam Types",
        "R1: Penipuan Uang Muka / Administrasi",
        "Lowongan Operator Produksi Pabrik Otomotif Karawang. Gaji 6,5 Juta. Bawa uang administrasi dan seragam Rp 350.000 saat interview besok pagi.",
        "HIGH",
        check_fn=lambda r: any(i["code"] == "R1" for i in r["detected_indicators"])
    )

    # 3.2 R2 - Gaji Fantastis Tanpa Syarat (Sinyal Peringatan)
    test_case(
        "Scam Types",
        "R2: Gaji Puluhan Juta Tanpa Skill/Pengalaman (Warning Signal)",
        "Dibutuhkan segera staf ketik online. Gaji 25 juta per bulan, tanpa syarat, tanpa pengalaman, cukup modal HP dan bisa mengetik. Siapa saja bisa bergabung.",
        "MEDIUM",
        check_fn=lambda r: any(i["code"] == "R2" for i in r["detected_indicators"])
    )

    # 3.3 R3 - Permintaan OTP / Kredensial Finansial
    test_case(
        "Scam Types",
        "R3: Permintaan Kode OTP / Password / PIN",
        "Selamat Anda lolos seleksi berkas. Untuk verifikasi data akun penerima gaji, sebutkan kode OTP yang masuk ke SMS HP Anda sekarang juga.",
        "HIGH",
        check_fn=lambda r: any(i["code"] == "R3" and i["confidence"] >= 0.9 for i in r["detected_indicators"])
    )

    # 3.4 R6 - Skema Top Up Modal / Tugas Berantai
    test_case(
        "Scam Types",
        "R6: Penipuan Top-Up Saldo Tugas Like & Subscribe",
        "Kerja sampingan dari rumah, tugas like & subscribe YouTube. Komisi 50rb per video. Wajib top up saldo deposit awal 500rb, modal akan dikembalikan beserta komisi setelah tugas selesai. Pasti profit.",
        "HIGH",
        check_fn=lambda r: any(i["code"] == "R6" for i in r["detected_indicators"])
    )

    # 3.5 R7 - Agen Travel & Tiket Fiktif / Talangan
    test_case(
        "Scam Types",
        "R7: Pemaksaan Tiket Melalui Agen Travel Tertentu",
        "Undangan Tes Wawancara PT Chevron Indonesia di Balikpapan. Peserta wajib memesan tiket pesawat dan akomodasi melalui agen travel yang kami tunjuk yaitu Buana Travel. Biaya keberangkatan ditanggung peserta dan akan direimburse.",
        "HIGH",
        check_fn=lambda r: any(i["code"] in ("R1", "R7") for i in r["detected_indicators"])
    )

    # 3.6 R9 - TPPO / Scam Hub Luar Negeri (Kamboja, Myanmar)
    test_case(
        "Scam Types",
        "R9: Penipuan CS Luar Negeri Kamboja Non-Prosedural",
        "Loker Luar Negeri Kamboja untuk posisi Customer Service Typing online. Gaji $2000 per bulan, tanpa syarat bahasa Inggris, fly in jalur khusus tanpa visa kerja, biaya tiket potong gaji.",
        "HIGH",
        check_fn=lambda r: any(i["code"] == "R9" for i in r["detected_indicators"])
    )

    # 3.7 R10 - Tekanan Waktu Ekstrem + Aksi Berisiko
    test_case(
        "Scam Types",
        "R10: Urgensi Kuota Terakhir & Ancaman Hangus",
        "Lowongan BUMN terbatas! Hanya tersisa 1 slot terakhir hari ini juga. Segera transfer biaya registrasi Rp 150.000 sekarang juga sebelum posisi Anda dialihkan ke kandidat lain!",
        "HIGH",
        check_fn=lambda r: any(i["code"] == "R10" for i in r["detected_indicators"])
    )

    print("\n--- [KATEGORI 4: UJI KETAHANAN EDGE CASES & ANTI-FALSE-POSITIVE] ---")
    
    # 4.1 Kalimat Disclaimer Resmi Tidak Boleh Picu False Positive
    test_case(
        "Edge Cases",
        "Lowongan Resmi Berisi Kata 'Penipuan' dan 'Tanpa Biaya' (Disclaimer Immunity)",
        "PT Telekomunikasi Indonesia Tbk (Telkom) membuka Rekrutmen Officer Development Program 2026. Penempatan seluruh Indonesia. Syarat: S1 Teknik/Informatika. Pendaftaran hanya melalui situs resmi https://careers.telkom.co.id. PERINGATAN: Telkom tidak pernah memungut biaya apa pun dalam proses rekrutmen. Waspada terhadap penipuan yang mengatasnamakan manajemen Telkom.",
        "LOW",
        check_fn=lambda r: (r["risk_score"] < 25 and len(r["detected_indicators"]) == 0, "Disclaimer tidak boleh memicu indikator R1/R4")
    )

    # 4.2 Teks Sangat Panjang (>20.000 Karakter)
    long_text = "Lowongan Kerja PT Sejahtera Bersama. Posisi Staf Gudang. Syarat: SMA sederajat. Lokasi: Bekasi.\n" + ("Tugas harian meliputi pengecekan stok barang di gudang. " * 600) + "\nKirim lamaran ke hrd@sejahterabersama.co.id"
    test_case(
        "Edge Cases",
        "Teks Sangat Panjang (Truncation & Stability Test)",
        long_text,
        "LOW",
        check_fn=lambda r: (r["risk_score"] is not None and isinstance(r["risk_score"], int), "Harus diproses tanpa error")
    )

    # 4.3 Teks Bersih dengan Format Angka COD / Setoran Kasir (Bukan Scam Fee)
    test_case(
        "Edge Cases",
        "Deskripsi Pekerjaan Kasir / Kurir Menyebut 'Setor Uang Penjualan'",
        "Dibutuhkan Kasir Toko Retail. Tanggung jawab: melayani pembayaran konsumen, membuat laporan kas, dan menyetor uang hasil penjualan harian ke rekening toko. Gaji UMK + bonus. Lamar di toko Jl. Veteran No. 10.",
        "LOW",
        check_fn=lambda r: (len([i for i in r["detected_indicators"] if i["code"] == "R1"]) == 0, "Setor uang hasil penjualan bukan R1")
    )

    # 4.4 Teks Multibahasa / Unicode / Karakter Emoji
    test_case(
        "Edge Cases",
        "Teks dengan Banyak Emoji & Unicode",
        "🔥 LOKER TERBARU 2026 🔥\n✨ Posisi: Social Media Specialist ✨\n📍 Lokasi: Jakarta Barat (Hybrid)\n💼 Syarat: Min. D3/S1, menguasai Canva & CapCut\n💰 Gaji: Rp 5.000.000 - 7.000.000\n📩 Kirim portfolio ke: talent@kreasidigital.id\n⚠️ Tidak ada pungutan biaya apapun ⚠️",
        "LOW",
        check_fn=lambda r: (r["risk_level"] == "LOW", "Harus LOW")
    )

    print("\n--- [KATEGORI 5: VALIDASI KELENGKAPAN OUTPUT & KONTRAK SCHEMA WEB] ---")
    
    sample_res = engine.analyze("Lowongan kerja PT Astra International Tbk melalui https://career.astra.co.id", mode="hybrid")
    required_keys = [
        "risk_score", "risk_level", "detected_indicators", "evidence",
        "dimension_scores", "verification_status", "context_flags",
        "risk_explanation", "recommended_actions", "disclaimer",
        # Backward compatibility fields
        "message", "dimensions", "indicators", "recommendations",
        "verification_checklist", "context", "meta"
    ]
    
    schema_ok = True
    missing_keys = []
    for k in required_keys:
        if k not in sample_res:
            schema_ok = False
            missing_keys.append(k)
            
    total_tests += 1
    test_categories.setdefault("Schema Contract", {"total": 0, "passed": 0})
    test_categories["Schema Contract"]["total"] += 1
    if schema_ok:
        passed_tests += 1
        test_categories["Schema Contract"]["passed"] += 1
        print("[PASS] | Schema Contract -> Kelengkapan Seluruh Kunci Output JSON untuk Web")
    else:
        print(f"[FAIL] | Schema Contract -> Kunci yang hilang: {missing_keys}")

    # Validasi Tipe Data Schema
    type_ok = (
        isinstance(sample_res["risk_score"], int) and
        isinstance(sample_res["risk_level"], str) and
        isinstance(sample_res["detected_indicators"], list) and
        isinstance(sample_res["dimension_scores"], dict) and
        isinstance(sample_res["verification_status"], dict) and
        isinstance(sample_res["recommended_actions"], list) and
        isinstance(sample_res["disclaimer"], str) and
        len(sample_res["disclaimer"]) > 10
    )
    total_tests += 1
    test_categories["Schema Contract"]["total"] += 1
    if type_ok:
        passed_tests += 1
        test_categories["Schema Contract"]["passed"] += 1
        print("[PASS] | Schema Contract -> Validasi Tipe Data & Format JSON")
    else:
        print("[FAIL] | Schema Contract -> Tipe data pada respons tidak sesuai")

    print("\n" + "=" * 75)
    print("                    RINGKASAN QUALITY CHECK")
    print("=" * 75)
    for cat, stats in test_categories.items():
        rate = (stats["passed"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        print(f" {cat:<22}: {stats['passed']}/{stats['total']} Lulus ({rate:.1f}%)")
    print("-" * 75)
    print(f" TOTAL PENGUJIAN       : {passed_tests}/{total_tests} Lulus ({(passed_tests/total_tests)*100:.1f}%)")
    print("=" * 75 + "\n")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_quality_check()
    sys.exit(0 if success else 1)
