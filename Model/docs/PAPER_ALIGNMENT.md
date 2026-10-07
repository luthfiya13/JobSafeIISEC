# Keselarasan Paper ↔ Model v3 (perubahan yang harus ditulis ulang di paper)
| Paper (draft) | Model v3 | Alasan |
|---|---|---|
| Satu Hard Flag (R1,R4,R6,R7,R9) → S=100% | Noisy-OR + floor rule untuk kombinasi kritis | Hard-bypass membuat UMKM Gmail/shortlink = 100% (FP 16%) dan rawan klaim UU ITE |
| R4 = email gratisan/anonim | R4 = pencatutan employer / domain tak sesuai kanal resmi (butuh klaim employer) | Gmail & UMKM bukan indikasi penipuan |
| R7 = travel/akomodasi | R7 = travel **terikat** + biaya/utang | Fasilitas mess/tiket sah |
| R8 = WA/Telegram pribadi (soft 10%) | R8 = rekruter menghambat verifikasi / kontak asing (konteks, tanpa floor) | WA pribadi umum di UMKM |
| Ambang S≥40% HIGH | LOW<25, MEDIUM<60, HIGH≥60 (bootstrap) | Skala baru; rekalibrasi |
| "Aman/terverifikasi" untuk LOW | "Tidak ditemukan indikator" | Engine tak memverifikasi |
Tetap sama: R1–R10 (slot kode), explainable output, dasar hukum (UU PDP, UU ITE 27A/28, TPPO), pemetaan Tadlis/Gharar/Hifzh al-Mal/an-Nafs (kini ada di `config.indicators[*].syariah`), arsitektur Next.js + FastAPI.
Bagian yang wajib ditulis ulang: §3.3 (bobot & rumus), Tabel 3.1/3.2, §4.3 (hasil evaluasi setelah label independen), Lampiran A–D.
