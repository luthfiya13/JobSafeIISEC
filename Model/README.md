# JOBSAFE Model v3.0 — Rule-first Explainable Risk Engine

Output produksi: **LOW / MEDIUM / HIGH / INSUFFICIENT_INPUT** (bukan vonis "penipu/asli").

## Jalankan
```bash
pip install -r requirements.txt
python tests/smoke_tests.py                     # 32 kasus regresi, harus FAILED: 0
uvicorn scripts.fastapi_app:app --reload        # POST /analyze , GET /health
```
Catatan: endpoint FastAPI belum dijalankan di lingkungan audit (paket fastapi tidak terpasang); engine inti & tes sudah diuji.

## Alur
teks (OCR/paste) → bersihkan, **buang kalimat disclaimer** → deteksi R1–R10 (confidence 0–1 + bukti) →
skor = **noisy-OR(base_weight × confidence)** → **floor rules** (kombinasi kritis) → LOW(<25) / MEDIUM(25–<60) / HIGH(≥60) → penjelasan + dasar hukum + dasar syariah + rekomendasi.

## Kontrak API untuk tim web
`POST /analyze` body: `{"text": "...", "url": null}`
Respons: `risk_score` (0–100 / null bila INSUFFICIENT_INPUT), `risk_level`, `message`, `dimensions{}`,
`indicators[] {code,name,confidence,strength(STRONG|MODERATE|WEAK),evidence,reason,legal_basis,syariah_basis}`,
`recommendations[]`, `verification_checklist[]`, `context{}`, `disclaimer`, `meta{engine_version,floors_applied,base_score,...}`.
UI wajib menampilkan `disclaimer`; jangan pernah menampilkan kata "penipu". Tangani `INSUFFICIENT_INPUT` (abu-abu).
OCR (EasyOCR) dilakukan di luar `analyze()`; hasil teksnya dikirim ke endpoint. Jangan simpan/log teks pengguna (UU PDP).

## Data (`data/`)
| File | Fungsi | Boleh dipakai untuk |
|---|---|---|
| `gold_regression_cases.csv` | 32 kasus SINTETIK buatan tangan | unit/regression test saja — **bukan** angka akurasi paper |
| `REAL_800_Broad_Candidates.csv` | 800 posting Glints, belum berlabel | stress-test false positive; calon anotasi |
| `SCAM_ADVISORY_EVIDENCE_LIBRARY_clean.csv` | 54 kasus advisory (+1 baris agregat) | referensi bukti/pemetaan R; bukan data latih |
| `PAPER_50_POSTER_TEMPLATE.csv` | kerangka 50 poster paper (OCR + label independen belum diisi) | **evaluasi utama paper** |

## Langkah berikutnya (urut)
1. Jalankan `scripts/ocr_extract.py` pada 50 poster → isi `ocr_text`, koreksi manual.
2. Beri `gold_level` independen (lihat `docs/ANNOTATION_GUIDE.md`), 2 anotator, hitung kappa.
3. `python scripts/evaluate.py --csv data/PAPER_50_POSTER_TEMPLATE.csv`.
4. Verifikasi manual `config/official_domains.json` (seed list).
5. ML (TF-IDF+LR) ditunda: tidak ada contoh posting MEDIUM/HIGH yang cukup. Lihat `docs/AUDIT_REPORT.md`.
