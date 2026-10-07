# Laporan Audit v2.1 → v3.0

## A. Kesalahan FATAL pada engine v2.1 (terbukti dengan uji)
1. **`escalations` di config tidak pernah dipakai** — engine membaca `floor_rules` bila ada, sehingga aturan `exploitation_cluster` mati. Akibatnya skema Kamboja ("jalur khusus + kirim KTP via WA + gaji $2000") hanya MEDIUM 40. Penyebab kedua: R3 diberi 0.48 (<ambang 0.5). → v3: satu daftar aturan, R9 kuat langsung HIGH.
2. **R4 memicu pada kalimat peringatan**: "Waspada akun palsu mengatasnamakan perusahaan kami…" (posting sah) → MEDIUM 35. → v3: kalimat disclaimer dibuang sebelum deteksi.
3. **R3 memicu pada kata "mobile banking"/"PIN"** tanpa kata kerja permintaan: lowongan CS Bank sah → MEDIUM. → v3: butuh kata kerja meminta; SIM dikeluarkan (syarat kerja kurir).
4. **Alias organisasi cocok sebagai substring** ("bri" ⊂ "fabrication/brief") + regex URL menganggap `Jl.Sudirman` sebagai domain → R4 palsu. → v3: word-boundary, TLD whitelist, org harus berperan sebagai employer (disebut di awal/dekat "rekrutmen/lowongan/PT").
5. **Agregasi per-dimensi (maks 20% per dimensi) membuat skor dasar tak bermakna**: satu R1 kuat hanya 18; semua keputusan ditentukan floor. → v3: noisy-OR terbobot + floor untuk kombinasi kritis.
6. **R1 salah pada "Setor Uang COD"** (tugas kurir sah) dan R10 pada "Perseroan **Terbatas**". → diperbaiki.
7. **R1 buta pada variasi**: "harap membayar uang administrasi" lolos sebagai LOW. → pola diperluas.
8. **Input pendek / hanya link dinilai MEDIUM 25** (menyesatkan). → `INSUFFICIENT_INPUT`.
9. `train_risk_model.py` tak bisa jalan: data 800 hanya akan berisi LOW (butuh ≥3 kelas); `multi_class` sudah usang di sklearn terbaru. → ML ditunda; skrip dihapus dari paket.
10. `verification` di respons hardcode "UNVERIFIED" tanpa makna. → diganti `verification_checklist` + `disclaimer`.
11. Pesan "LOW = Aman/terverifikasi" (paper) menyesatkan: engine tak memverifikasi apa pun. → "tidak ditemukan indikator", bukan jaminan.

## B. Masalah DATASET
| Masalah | Tingkat | Tindakan |
|---|---|---|
| 800 REAL hanya dari Glints; **tidak ada URL, email, nomor HP** (sudah dibersihkan) → R4/R8/shortlink tak pernah teruji pada data nyata | Tinggi | Dicatat sebagai `data_caveat`; evaluasi utama harus pada 50 poster paper |
| 76% posting bertanggal Mei–Juni 2026 (bias waktu) | Sedang | dicatat |
| 800 REAL belum berlabel — bukan ground truth LOW | Tinggi | sampel 200 untuk anotasi manusia, bukan label otomatis |
| Tidak ada satu pun contoh posting HIGH/MEDIUM berbentuk poster/teks iklan → klasifikasi 3 kelas tidak bisa dilatih | **Fatal untuk ML** | gunakan rule-first; ML hanya setelah ≥150 contoh berlabel/kelas |
| FAKE library: 55 baris (bukan 54), 1 baris agregat; kolom `label` berisi "GOLD/SILVER" pada 6 baris dan `label_confidence` kosong pada 5 baris | Sedang | dibersihkan (`case_role`, `confidence`, `use_for_case_eval`) |
| FAKE library memakai kode L/D/F/M/E tanpa legenda, bukan R1–R10 | Sedang | dipetakan heuristik → `expected_R_heuristic` (perlu tinjau manusia) |
| FAKE library ±90% kasus impersonasi (bias sumber: yang dibantah resmi), hanya 8 R1, 3 R9, 1 R6 | Sedang | jangan dipakai menyimpulkan prevalensi |
| Teks advisory ≠ teks posting (gaya berbeda) | Tinggi | tidak digabung dengan 800 REAL (keputusan v2.1 dipertahankan) |
| 19 perusahaan muncul 2× | Ringan | `group_id` + split berbasis grup |

## C. Masalah pada ANOTASI di paper (Lampiran A/B) — wajib dibereskan sebelum submit
1. **Bobot tidak konsisten**: Tabel 3.1 berjumlah **105%** (15+10+8+10+7+15+10+10+15+5), padahal klaim 100%; Lampiran memakai bobot lain (R3=15, R8=5, R9=5, R5=10).
2. **Kode indikator dipakai salah di Tabel B**: shortlink bit.ly ditandai "R4 & R6"; AI-generated image ditandai "R7"; QR/WA ditandai "R1, R6"; "R8" disebut Hard-Rule padahal Soft. Definisi di Tabel 3.1 berbeda.
3. **Sampel #3 (PT Dash Elektrik)**: Tabel A = Data Primer (Scam), Tabel B = posting valid / False Positive. Jika valid, TP=24, bukan 25.
4. **File duplikat**: #8 dan #18 sama-sama `1000326451.jpg`.
5. **Ground truth sirkular**: ground truth dibuat "peneliti" memakai rubrik R1–R10 yang sama dengan engine → recall 100% hampir pasti. Label harus dari bukti eksternal + 2 anotator + kappa.
6. **Leakage sumber**: kelas Primer = poster Instagram/AI, kelas Sekunder = LinkedIn/Jobstreet; klaster kampanye sama (goletskerja.com ×4, updateinfoloker.id ×4, nomor +91 ×3) tersebar → model bisa belajar "sumber", bukan risiko.
7. **8 False Positive = 16%** disebabkan *desain* R4 (Gmail/shortlink = Hard Flag), bukan kebetulan. v3 membalik ini (Gmail/shortlink bukan risiko sendiri).
8. Presisi/Recall pada n=50 tanpa interval kepercayaan; hitung Wilson CI (script `evaluate.py`).
9. Abstrak masih berisi placeholder `[ISI SKOR…]`; ambang SUS saling bertentangan (50,9 / 70,8 / 68,0 / 70,9); angka SUS 82,5/77,5/75 tanpa data mentah.
10. Teks R6/R7 tertukar pada §4.3.1; klaim "tanpa False Negative/zero tolerance" terlalu kuat.
11. Paper menyebut "10 indikator tervalidasi" — belum ada validasi (uji kesepakatan pakar/CVI) yang dilaporkan.

## D. Batasan v3 yang jujur
- Rule-based regex: bahasa baru/typo OCR berat bisa lolos (FN); gold regression 32/32 **tidak** berarti akurat — kasus ditulis dan disetel oleh pengembang (sirkular).
- 800 REAL kini 800/800 LOW, tetapi aturan disetel setelah melihat temuan di data itu; gunakan `split_hint=HELDOUT_FP_CHECK` dan data baru untuk klaim.
- Daftar domain resmi hanya seed; R4 hanya berlaku untuk org dalam daftar.
- Ambang 25/60 masih bootstrap; kalibrasi pada data berlabel independen.
- Modul OCR belum diuji (EasyOCR tak tersedia di lingkungan audit).
