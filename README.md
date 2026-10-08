# JOBSAFE — Digital Job Risk Assessment Platform

> **"Kenali risikonya. Verifikasi informasinya."**

**JOBSAFE** adalah platform digital untuk membantu para pencari kerja, mahasiswa, dan masyarakat umum dalam menilai tingkat risiko suatu lowongan kerja digital secara mandiri, objektif, dan transparan.

Sistem tidak memberikan vonis mutlak (bukan klaim absolut bahwa suatu lowongan pasti penipuan atau pasti legal), melainkan memberikan **Risk Assessment** terukur yang mencakup:
1. **Risk Score (0–100)** dan **Tingkat Risiko** (Risiko Rendah, Risiko Sedang, Risiko Tinggi).
2. **Indikator yang Terdeteksi** dari 10 parameter risiko digital berbobot terstruktur (Total Bobot 100%).
3. **Bukti & Kutipan Kalimat** (*Evidence Snippet*) yang mendasari terpicunya suatu indikator.
4. **Alasan Edukatif** mengapa indikator tersebut perlu diwaspadai.
5. **Panduan Verifikasi Mandiri** berupa checklist interaktif sebelum mengambil keputusan untuk melamar.

---

## 🎨 Konsep Desain & Identitas Visual

- **Karakter Desain:** Modern, clean, elegan, profesional, mobile-first, dan ramah pengguna awam (non-intimidatif).
- **Palet Warna:**
  - **Primary Navy:** `#0f172a` (Slate 900)
  - **Secondary Blue:** `#2563eb` (Blue 600)
  - **Background:** `#f8fafc` (Off-white / Slate 50)
  - **Teks Utama:** `#0f172a` (Deep Navy / Charcoal)
  - **Teks Sekunder:** `#64748b` (Slate 500)
  - **Indikator Risiko Rendah (Safe):** `#16a34a` (Emerald 600) / Skor 0–29
  - **Indikator Risiko Sedang (Attention):** `#f59e0b` (Amber 500) / Skor 30–69
  - **Indikator Risiko Tinggi (High):** `#dc2626` (Red 600) / Skor 70–100

---

## 👥 Pemisahan Dua Role Pengguna

### 1. Pengunjung / User (Tanpa Login & Privasi Penuh)
- **Tanpa akun & tanpa registrasi**: Tidak meminta email, nomor HP, atau data pribadi pengunjung.
- **3 Pilihan Input Lowongan:**
  - **Tab 1 — Teks**: Tempel teks lowongan atau uji cepat dengan contoh lowongan (Risiko Tinggi, Sedang, Rendah).
  - **Tab 2 — Foto**: Unggah screenshot postingan lowongan (PNG, JPG, JPEG) dengan OCR text extraction.
  - **Tab 3 — Link**: Masukkan URL postingan web lowongan untuk diekstraksi secara otomatis (dengan fallback ramah jika link terproteksi).
- **Layar Analisis Progresif**: Animasi 5 tahap verifikasi data.
- **Dashboard Hasil Penilaian:**
  - Komponen **Risk Meter** berbentuk lingkaran/gauge interaktif.
  - **Ringkasan Temuan** sistem.
  - **10 Kartu Indikator Risiko** lengkap dengan status, bobot, dan modal detail bukti teks.
  - **Checklist Verifikasi Mandiri** interaktif.
  - Fitur cetak / simpan PDF hasil analisis.

### 2. Administrator (Terpisah & Terproteksi)
- **Halaman Login Admin**: `/admin/login` (Admin Area terisolasi, autentikasi aman dengan bcrypt dan JWT token).
- **Kredensial Default Demo**:
  - Email: `admin@jobsafe.id`
  - Password: `admin123`
- **Fitur Admin:**
  - **Dashboard Ringkasan** (`/admin/dashboard`): Kartu metrik total analisis, grafik distribusi risiko, frekuensi indikator teratas, dan tabel analisis terbaru.
  - **Riwayat Analisis** (`/admin/analyses`): Log pemindaian anonim, pencarian kata kunci, filter level risiko, dan modal detail kasus.
  - **Kelola Indikator** (`/admin/indicators`): Pengaturan bobot 10 indikator, toggle aktif/nonaktif, edit deskripsi, pemantauan total bobot real-time, serta peringatan otomatis jika total bobot $\neq$ 100%.
  - **Pengaturan Sistem** (`/admin/settings`): Ambang batas kategori risiko (threshold), nama aplikasi, dan modal konfirmasi simpan.

---

## 📊 10 Indikator Risiko Digital

| Kode | Nama Indikator | Bobot | Deskripsi Singkat |
| :--- | :--- | :---: | :--- |
| **R1** | **Biaya di Awal** | 15% | Permintaan biaya pendaftaran, deposit, pelatihan, materi, atau seragam sebelum bekerja. |
| **R2** | **Imbalan Tidak Wajar** | 10% | Janji penghasilan sangat tinggi (misal Rp500rb–Rp1jt/hari) dengan kualifikasi minimal / tanpa pengalaman. |
| **R3** | **Permintaan Dokumen Sensitif** | 15% | Permintaan foto KTP, selfie dengan KTP, atau buku tabungan sebelum proses seleksi sah. |
| **R4** | **Identitas Perusahaan Tidak Jelas** | 10% | Perusahaan anonim, tanpa alamat fisik terverifikasi, atau memakai email gratisan (@gmail/@yahoo). |
| **R5** | **Deskripsi Pekerjaan Tidak Jelas** | 10% | Uraian tugas ambigu, 'kerja santai apa saja', tanpa kriteria teknis yang jelas. |
| **R6** | **Skema Tugas Berantai** | 15% | Misi like medsos, subscribe channel, rating e-commerce bertingkat, atau top-up deposit saldo misi. |
| **R7** | **Perjalanan/Akomodasi Wajib** | 10% | Panggilan tes luar kota dengan kewajiban memesan tiket travel/hotel via agen yang ditunjuk panitia. |
| **R8** | **Kanal Komunikasi Tidak Resmi** | 5% | Seleksi dan instruksi hanya via kontak pribadi WhatsApp / Telegram tanpa domain perusahaan resmi. |
| **R9** | **Tawaran Kerja Luar Negeri Berisiko** | 5% | Tawaran luar negeri (Kamboja, dsb.) tanpa izin resmi P3MI / BP2MI atau menggunakan visa turis. |
| **R10**| **Urgensi Palsu** | 5% | Frasa tekanan batas waktu ('kuota terbatas', 'transfer sekarang', 'kesempatan terakhir'). |
| **TOTAL** | | **100%** | |

---

## 🛠️ Arsitektur Teknologi

```
JOBSAFE/
├── backend/                  # Python FastAPI Backend
│   ├── app/
│   │   ├── api/              # Endpoints: /api/analyze/*, /api/admin/*, /api/auth
│   │   ├── engine/           # Analyzer core, 10 indicators, OCR service, Web scraper
│   │   ├── database/         # SQLite database, migration, model queries
│   │   ├── config.py         # App configurations & risk thresholds
│   │   └── main.py           # FastAPI entrypoint & CORS middleware
│   └── requirements.txt
└── frontend/                 # Next.js 16 App Router (TypeScript + Tailwind CSS)
    ├── src/
    │   ├── app/
    │   │   ├── page.tsx      # Landing page (Hero, Risk meter mockup, Cara kerja, 10 indikator, Tentang)
    │   │   ├── periksa/      # Fitur periksa lowongan (Teks, Foto, Link) & Hasil Analisis
    │   │   └── admin/        # Portal Admin (Login, Dashboard, Analyses, Indicators, Settings)
    │   ├── components/       # RiskGauge, IndicatorCard, IndicatorModal, VerificationChecklist, Navbar, Footer, etc.
    │   └── lib/              # API clients & preset sample lowongan
```

---

## 🚀 Cara Menjalankan Aplikasi

### 1. Menjalankan Backend (FastAPI)
```bash
cd backend
# Buat dan aktifkan virtual environment (menggunakan uv atau python -m venv)
uv venv
.venv\Scripts\activate

# Install dependensi
uv pip install -r requirements.txt

# Jalankan server FastAPI
python -m uvicorn app.main:app --port 8000 --reload
```
API akan aktif di: `http://127.0.0.1:8000` (Dokumentasi Swagger di `http://127.0.0.1:8000/docs`).

### 2. Menjalankan Frontend (Next.js)
```bash
cd frontend
# Install dependensi (jika baru pertama kali clone)
npm install

# Jalankan server development Next.js
npm run dev
```
Buka browser di: `http://localhost:3000`.

Frontend meneruskan seluruh request API ke FastAPI melalui route server-side. Untuk deployment, set
`BACKEND_API_URL` ke URL backend yang berakhiran `/api` (contoh: `https://api.example.com/api`).
Backend membutuhkan dependensi engine hybrid dari `backend/requirements.txt`; jika paket ML belum tersedia,
API tetap berjalan dengan rule engine kompatibilitas dan melaporkan mode fallback pada metadata hasil.
