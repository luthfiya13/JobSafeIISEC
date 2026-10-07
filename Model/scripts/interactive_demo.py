#!/usr/bin/env python3
"""
Interactive Testing Playground for JOBSAFE Risk Engine.
Allows you to input/paste any job text and view real-time explainable risk assessment.
"""
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from jobsafe import JobsafeHybridEngine

def print_result(res: dict):
    print("\n" + "=" * 65)
    print(f"HASIL ANALISIS RISIKO JOBSAFE (v{res['meta']['engine_version']})")
    print("=" * 65)
    
    level = res["risk_level"]
    score = res["risk_score"]
    color = "🔴" if level == "HIGH" else ("🟡" if level == "MEDIUM" else ("🟢" if level == "LOW" else "⚪"))
    
    print(f"Status Risiko : {color} {level} (Skor: {score}/100)")
    print(f"Mode Engine   : {res['meta'].get('hybrid_mode', 'hybrid').upper()}")
    print(f"Pesan Utama   : {res['message']}")
    
    verif = res.get("verification_status", {})
    print(f"\n[Verifikasi Entitas]")
    print(f"  - Status     : {verif.get('status', 'UNVERIFIED')}")
    print(f"  - Detail     : {verif.get('details', '-')}")
    
    inds = res.get("detected_indicators", [])
    print(f"\n[Indikator Risiko Terdeteksi ({len(inds)})]")
    if not inds:
        print("  - Tidak ada indikator risiko mencurigakan yang terdeteksi.")
    else:
        for i in inds:
            print(f"  * [{i['code']}] {i['name']} (Kekuatan: {i['strength']}, Conf: {i['confidence']})")
            print(f"    Bukti   : \"{i['evidence']}\"")
            print(f"    Alasan  : {i['reason']}")
            if i.get("legal_basis") and i["legal_basis"] != "-":
                print(f"    Hukum   : {i['legal_basis']}")
            if i.get("syariah_basis"):
                print(f"    Syariah : {i['syariah_basis']}")

    print(f"\n[Skor Dimensi Risiko]")
    for dim, dscore in res.get("dimension_scores", {}).items():
        print(f"  - {dim:<22} : {dscore}%")

    print(f"\n[Rekomendasi Tindakan]")
    for r in res.get("recommended_actions", []):
        print(f"  ✓ {r}")

    print(f"\n[Disclaimer]")
    print(f"  {res['disclaimer']}")
    print("=" * 65 + "\n")

def main():
    print("Memuat JOBSAFE Hybrid Engine...")
    engine = JobsafeHybridEngine()
    print("Engine siap! Masukkan teks lowongan untuk diuji.")
    print("Ketik 'exit' atau 'keluar' untuk mengakhiri program.\n")
    
    preset_cases = [
        ("1. Lowongan Penipuan Uang Muka (Scam Fee)", "Dibutuhkan 20 Staff Admin PT Maju Jaya, gaji 8 juta. Wajib transfer biaya pendaftaran Rp 250.000 untuk seragam kerja. Hubungi WA 081234567890. Kuota terbatas!"),
        ("2. Lowongan Penipuan Tugas Like & Subscribe (Task Scam)", "Kerja sampingan dari rumah, tugas cukup like dan subscribe YouTube, komisi Rp 50.000 per tugas. Wajib deposit modal awal 200rb untuk buka akun tugas. Pasti untung."),
        ("3. Pencatutan BUMN + Domain Palsu (Impersonation)", "Lowongan BUMN PT Pertamina 2026 posisi teller dan admin. Pendaftaran melalui http://goletskerja.com/pertamina. Segera kirim foto KTP."),
        ("4. Lowongan UMKM Sah dengan Kontak WA (Legitimate Informal)", "Toko Kue Armindo Magelang butuh kasir toko. Syarat: min SMA, jujur, pengalaman 1 tahun. Kirim lamaran ke armindomagelang@gmail.com atau WA 082227187988. Gaji UMK Magelang. Gratis tanpa pungutan biaya.")
    ]

    while True:
        print("-" * 65)
        print("PILIHAN:")
        print(" [0] Ketik / Tempel teks lowongan sendiri")
        for idx, (label, _) in enumerate(preset_cases, 1):
            print(f" [{idx}] Coba contoh: {label}")
        print(" [q] Keluar")
        
        choice = input("\nPilih nomor (0-4 atau q): ").strip().lower()
        if choice in ("q", "exit", "keluar"):
            print("Terima kasih telah menggunakan JOBSAFE.")
            break
            
        if choice in ("1", "2", "3", "4"):
            idx = int(choice) - 1
            label, sample_text = preset_cases[idx]
            print(f"\nMenguji contoh: {label}")
            print(f"Teks:\n\"{sample_text}\"")
            res = engine.analyze(sample_text, mode="hybrid")
            print_result(res)
        elif choice == "0" or choice == "":
            print("\nTempel teks lowongan kerja (tekan ENTER 2x setelah selesai):")
            lines = []
            while True:
                line = input()
                if not line and lines and not lines[-1]:
                    break
                lines.append(line)
            input_text = "\n".join(lines).strip()
            if not input_text:
                print("[!] Teks kosong.")
                continue
            res = engine.analyze(input_text, mode="hybrid")
            print_result(res)
        else:
            print("[!] Pilihan tidak valid.")

if __name__ == "__main__":
    main()
