# JOBSAFE: Penyelarasan Metodologis & Riset Ilmiah (Research Alignment)

Dokumen ini memetakan hubungan formal antara rancangan paper IISEC 2026, kerangka teori/hukum/syariah, baseline JOBSAFE v3, perbaikan sistem engine (Rule-First, ML, Hybrid), status data empiris, serta protokol eksperimen wajib.

---

## 1. Research Objective (Tujuan Penelitian)
1. **Merumuskan & Mengoperasionalkan Kerangka Risiko 10 Indikator (R1–R10)**: Mengembangkan taksonomi risiko penipuan rekrutmen digital (*Online Recruitment Fraud* / ORF) yang mencakup 5 dimensi: Finansial, Data & Identitas, Keabsahan & Deception, Eksploitasi & Keselamatan Fisik, serta Manipulasi Psikologis, dengan landasan yuridis (UU PDP No. 27/2022, UU ITE No. 1/2024, Permenaker No. 39/2016, UU No. 21/2007 TPPO) dan Maqasid Syariah (*Hifzh al-Mal, Hifzh an-Nafs, Hifzh al-'Irdh*).
2. **Mengembangkan Hybrid Explainable Risk Assessment Engine**: Membangun sistem penilaian risiko ordinal (*LOW, MEDIUM, HIGH*) yang context-aware, conservative, tidak mudah terpicu *false positive* pada entitas sah (UMKM, startup, kanal perpesanan informal), serta memberikan penjelasan rasional (*evidence & reason*) dan rekomendasi verifikasi independen (*tabayyun*).
3. **Menyediakan Lapisan Verifikasi Entitas (Verification Layer)**: Mengklasifikasikan status keabsahan saluran perekrut ke dalam 3 kondisi diskret (*VERIFIED, UNVERIFIED, CONTRADICTORY*) tanpa secara gegabah mendiskualifikasi entitas non-terdaftar sebagai penipuan.
4. **Membangun Pipeline Evaluasi & Benchmark Ilmiah yang Terbebas dari Kebocoran Data (Data Leakage)**: Menyusun pengujian empiris multi-metrik (Macro F1, Balanced Accuracy, High-Risk Precision/Recall, Slice Analysis, Wilson 95% CI) berbasis *GroupKFold* dan protokol anotasi ganda (*Inter-Annotator Agreement* Cohen's Kappa).

---

## 2. Research Gap (Kesenjangan Riset)
1. **Reduksionisme Klasifikasi Biner Kaku (Real vs Fake)**: Mayoritas literatur sebelumnya memperlakukan deteksi loker palsu sebagai binary text classification tanpa nuansa risiko. Model biner mengabaikan fakta bahwa loker sah di negara berkembang sering menggunakan kanal informal (WhatsApp, Gmail, tanpa website resmi), sehingga memicu tingkat *False Positive* yang tinggi.
2. **Ketiadaan Prinsip Minimisasi Data & Explainability**: Model *black-box* (misal deep learning mentah / Fraud-BERT) tidak memberikan justifikasi yuridis mengapa suatu loker berbahaya, serta sering mewajibkan penyimpanan data pengguna yang melanggar prinsip kepatuhan privasi (UU PDP).
3. **Data Leakage & Inkompatibilitas Genre Teks**: Penelitian terdahulu sering mencampurkan teks iklan lowongan nyata dengan teks narasi klarifikasi/advisory penipuan (berita bantahan BUMN), yang menyebabkan model hanya belajar gaya penulisan berita/klarifikasi (*genre leakage*), bukan karakteristik risiko lowongan kerja.
4. **Dominasi Indikator Finansial Tunggal**: Banyak sistem hanya mendeteksi kata kunci biaya/uang pendaftaran, sementara modus eksploitasi modern (seperti skema tugas *like-and-subscribe*, migrasi non-prosedural ke pusat penipuan daring Kamboja/Myanmar/Laos, dan pemanenan identitas KTP/OTP) luput dari deteksi dini.

---

## 3. Kontribusi Ilmiah yang Benar-Benar Didukung Sistem
- [x] **Taksonomi R1–R10 Terintegrasi**: 10 indikator terpetakan pada 5 dimensi risiko dengan rujukan yuridis nasional dan Maqasid Syariah.
- [x] **Rule-First Engine dengan Interaction Floors**: Menggabungkan probabilitas agregasi *noisy-OR* dengan *hard floor bypass* untuk indikator fatal (R1 uang muka, R3 kredensial OTP/PIN, R6 tugas top-up berantai, R9 TPPO/scam hubs).
- [x] **Context-Awareness & Disclaimer Stripping**: Mekanisme prapemrosesan teks yang membedakan disclaimer anti-penipuan dari indikasi kejahatan, serta mengecualikan istilah operasional sah (seperti uang dinas, makan siang gratis, setoran COD kurir, syarat SIM/SKCK).
- [x] **Verification Layer Tiga-Status (*VERIFIED / UNVERIFIED / CONTRADICTORY*)**: Pengujian otentisitas domain dan email terhadap direktori instansi dan platform rekrutmen resmi.
- [x] **Pipeline Hybrid & ML Defensibel**: Kombinasi TF-IDF word (1-2) + char (3-5) n-gram dengan *Regularized/Calibrated Logistic Regression* dan *Conservative Floor Gating*.
- [x] **Pipeline Anotasi Terstruktur**: Alat adjudikasi Cohen's Kappa, penghitungan interval kepercayaan Wilson 95%, dan analisis irisan (*slice analysis*).

---

## 4. Kondisi Baseline V3
Baseline JOBSAFE v3 telah berhasil memperbaiki kesalahan fatal pada v2.1:
1. Menyatukan `floor_rules` agar aturan kritis langsung menaikkan skor ke level aman minimum.
2. Mengabaikan kalimat disclaimer anti-penipuan sebelum pemindaian kata kunci.
3. Memperbaiki pencocokan batas kata (*word boundary*) untuk mencegah sub-kata seperti `"bri"` dalam `"fabrication"` atau alamat jalan `"Jl.Sudirman"` memicu alarm palsu.
4. Menghapus ketergantungan pada model ML yang dilatih tanpa label risiko.

---

## 5. Kelemahan Baseline V3 yang Diidentifikasi
1. **Ketiadaan Lapisan Verifikasi Terstruktur**: Output v3 sebelumnya hanya menyajikan `verification_checklist` statis tanpa status diskret (*VERIFIED, UNVERIFIED, CONTRADICTORY*).
2. **Kerapuhan Pola Peran Lowongan (R5)**: Teks lowongan singkat yang memuat fasilitas seperti "uang dinas" atau "makan siang gratis" sempat memicu R5 akibat belum terbacanya kata kerja pembuka "membuka lowongan" atau nama posisi umum.
3. **Format Output Belum Sepenuhnya Terstandardisasi**: Kunci-kunci evaluasi frontend dan audit riset (seperti `detected_indicators`, `risk_explanation`, `verification_status`) tersebar dalam format bervariasi.
4. **Ketiadaan Pipeline Pelatihan & Evaluasi ML Terpadu**: Belum tersedianya modul ML terlatih dengan validasi silang bebas kebocoran (*GroupKFold*).

---

## 6. Perbaikan Teknis & Metodologis yang Diterapkan
1. **Modul `jobsafe/verification.py`**:
   - Mengevaluasi konsistensi entitas yang diklaim terhadap `official_domains.json`.
   - Mengembalikan status `VERIFIED` (bila cocok dengan portal resmi/platform terpercaya), `CONTRADICTORY` (bila mencatut entitas besar tetapi mengarahkan pendaftaran ke situs anonim/email gratisan), atau `UNVERIFIED` (untuk UMKM/startup independen).
   - Memastikan `UNVERIFIED` tidak pernah menaikkan risiko menjadi `HIGH` secara otomatis.
2. **Penyempurnaan Regex `jobsafe/rules.py`**:
   - Memperluas deteksi peran kerja (`membuka lowongan`, `staf`, `operator`, `kurir`, dll.) dan konteks kompensasi/fasilitas (`uang dinas`, `fasilitas gratis`, `insentif`, `mess`).
   - Memperkuat ketahanan terhadap nama domain perusahaan independen (seperti `Herpil.id`).
3. **Standardisasi Output `jobsafe/engine.py`**:
   - Menyediakan skema terpadu: `risk_score`, `risk_level`, `detected_indicators`, `evidence`, `dimension_scores`, `verification_status`, `context_flags`, `risk_explanation`, `recommended_actions`, `disclaimer`, sembari mempertahankan *backward compatibility* penuh.
4. **Modul ML & Hybrid (`jobsafe/ml_model.py` & `jobsafe/hybrid_engine.py`)**:
   - Ekstraktor fitur gabungan TF-IDF kata (1-2 n-gram), karakter (3-5 n-gram), dan fitur metadata struktural (rasio huruf kapital, panjang teks, entitas kontak).
   - Pengklasifikasi terkalibrasi (*Calibrated Logistic Regression*) dengan *Conservative Gating Override* (sinyal aturan kritis tidak dapat diturunkan oleh ML).
5. **Skrip Evaluasi & Anotasi Reproducible (`scripts/evaluate.py`, `scripts/prepare_annotation_dataset.py`, `scripts/adjudicate_annotations.py`, `scripts/audit_data_leakage.py`)**:
   - Mendukung evaluasi mode `rule_only`, `ml_only`, dan `hybrid`.
   - Menghitung Wilson 95% Confidence Intervals untuk seluruh metrik biner & ordinal.
   - Melakukan *slice analysis* otomatis per kategori entitas, panjang teks, dan status verifikasi.

---

## 7. Metode Final yang Direkomendasikan
Arsitektur final yang direkomendasikan untuk riset dan implementasi produksi adalah **Hybrid Risk Engine (Rule-First + Calibrated ML with Conservative Gating)**:
- **Jalur Utama (Safety-Critical Override)**: Aturan *Hard Floor Bypass* (R1, R3 kredensial, R6 tugas berantai, R9 TPPO) dan *Verification Layer* (`CONTRADICTORY`) bertindak sebagai pelindung mutlak agar kasus penipuan fatal tidak pernah diloloskan.
- **Jalur Statistik (Calibrated ML Probabilities)**: Untuk lowongan dengan pola tidak terstruktur atau variasi leksikal halus, model ML memberikan bobot probabilitas terkalibrasi guna memperkaya skor risiko ordinal.
- **Explainability**: Setiap keputusan selalu disertai bukti tekstual (*evidence snippet*), rujukan regulasi ketenagakerjaan/privasi, dan dasar maqasid syariah.

---

## 8. Status Data yang Tersedia
| Nama File | Jumlah Sampel | Sifat Data | Status & Fungsi |
|---|---|---|---|
| `data/gold_regression_cases.csv` | 32 kasus | Sintetik terkurasi | Kasus uji regresi unit & integrasi (bukan dasar klaim akurasi populasi paper). |
| `data/REAL_800_Broad_Candidates.csv` | 800 kasus | Riil (Glints Scraping) | Kumpulan kandidat perak lintas 16 sektor; teks telah disanitasi kontak; sumber sampling anotasi manusia. |
| `data/SCAM_ADVISORY_EVIDENCE_LIBRARY_clean.csv` | 55 baris | Riil (Advisory/Bantahan) | Basis pengetahuan modus penipuan; TIDAK boleh dicampur untuk klasifikasi biner karena perbedaan genre. |
| `data/PAPER_50_POSTER_TEMPLATE.csv` | 50 poster | Riil (25 Primer + 25 Sekunder) | Kerangka dataset evaluasi utama paper (memerlukan pengisian teks OCR & label independen). |
| `data/risk_annotation_template.csv` | 96 sampel | Riil terstratifikasi | Sampel siap anotasi untuk pengujian kesepakatan antar-anotator (*inter-annotator agreement*). |

---

## 9. Data yang Belum Memiliki Gold Label Independen
- **800 Data Glints (`REAL_800_Broad_Candidates.csv`)**: Data ini adalah kandidat lowongan kerja riil, namun belum dianotasi secara ganda oleh dua pakar independen. Mengasumsikan seluruh 800 data sebagai `LOW` secara apriori adalah bias metodologis (*silver label assumption*).
- **50 Poster Paper (`PAPER_50_POSTER_TEMPLATE.csv`)**: Teks hasil ekstraksi OCR dan pelabelan ganda independen (2 anotator + uji Kappa) wajib diselesaikan sebelum angka performa akhir dimasukkan ke naskah final paper.

---

## 10. Protokol Evaluasi yang Harus Dijalankan
1. **Anotasi Independen**: Dua annotator memberi label `LOW / MEDIUM / HIGH` dan centang R1–R10 pada dataset 50 poster tanpa melihat hasil prediksi sistem.
2. **Pengujian Reliabilitas Anotasi**: Jalankan `scripts/adjudicate_annotations.py` untuk menghitung nilai *Cohen's Kappa* (target $\kappa \ge 0.70$).
3. **Eksekusi Evaluasi Multi-Metrik**: Jalankan `scripts/evaluate.py --csv data/PAPER_50_POSTER_TEMPLATE.csv --mode hybrid`.
4. **Pelaporan Interval Kepercayaan (Wilson 95% CI)**: Setiap metrik akurasi, presisi, recall, dan FPR wajib dilaporkan beserta rentang CI-nya untuk mengantisipasi ketidakpastian sampel $N=50$.
5. **Analisis Irisan (Slice Analysis)**: Evaluasi performa sistem pada segmen spesifik: UMKM/startup, penggunaan email gratisan, penawaran gaji tinggi, dan kontak WhatsApp.

---

## 11. Catatan Kritis & Ketidaksesuaian Naskah Paper Saat Ini
Berikut adalah poin-poin dalam draf paper IISEC 2026 yang wajib disesuaikan sebelum naskah final dikirimkan:
1. **Ketidakkonsistenan Bobot Tabel 3.1**: Total bobot indikator di Tabel 3.1 berjumlah 105% (15+10+8+10+7+15+10+10+15+5). Harus diperbaiki menjadi tepat 100% atau diselaraskan dengan bobot *noisy-OR* engine v3.
2. **Klaim Presisi/Recall 100% Zero False Negative**: Klaim zero false negative pada $N=50$ tanpa interval kepercayaan rentan terhadap kritik penguji. Wajib menyertakan Wilson CI (misal: Recall 100.0%, 95% CI: [86.7% - 100.0%]).
3. **Kontradiksi Kasus #3 (PT Dash Elektrik)**: Di Tabel A terdaftar sebagai Data Primer (Scam), namun di Tabel B disebut sebagai data valid / False Positive. Harus dipastikan status faktualnya berdasarkan bukti verifikasi eksternal.
4. **Duplikasi File Gambar**: Kasus #8 dan #18 keduanya merujuk ke file gambar yang sama (`1000326451.jpg`). File #18 harus diganti dengan sampel poster unik.
5. **Placeholder Skor SUS**: Nilai rata-rata SUS pada Abstrak masih berupa placeholder `[ISI SKOR, misal: 81,5]`. Wajib diisi dari data tabulasi kuesioner 30 responden yang sesungguhnya.
6. **Perancuan Label Indikator pada Lampiran Tabel B**: Beberapa indikator di Tabel B ditandai tidak sesuai definisi Tabel 3.1 (misal shortlink ditandai R4 & R6; gambar AI ditandai R7). Wajib diselaraskan kembali ke definisi R1–R10.

---

## 12. Eksperimen Wajib Sebelum Naskah Paper Final
1. **Langkah 1**: Ekstraksi OCR lengkap untuk seluruh 50 poster menggunakan `scripts/ocr_extract.py` dan koreksi manual terhadap kesalahan pembacaan teks OCR.
2. **Langkah 2**: Pelabelan independen oleh 2 annotator pada `data/PAPER_50_POSTER_TEMPLATE.csv`.
3. **Langkah 3**: Eksekusi `scripts/adjudicate_annotations.py` untuk menghitung nilai Cohen's Kappa antar-penilai.
4. **Langkah 4**: Eksekusi `python scripts/evaluate.py --csv data/PAPER_50_POSTER_TEMPLATE.csv --mode hybrid --output_json docs/final_eval_report.json`.
5. **Langkah 5**: Pembaruan tabel matriks evaluasi dan kurva performa di naskah paper dengan data aktual hasil eksperimen.
