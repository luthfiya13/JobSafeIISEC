# Panduan Anotasi (label independen)
**Prinsip:** `gold_level` ditentukan dari BUKTI EKSTERNAL, bukan dari output engine dan bukan dari "ada/tidaknya rule yang kena".

| Level | Kriteria bukti |
|---|---|
| HIGH | Ada bantahan resmi employer/instansi (hoaks/komdigi/polri), ATAU permintaan bayar/top-up/OTP yang eksplisit di poster, ATAU lowongan luar negeri tanpa izin P3MI dengan sinyal eksploitasi |
| MEDIUM | Employer nyata tetapi kanal/izin tidak dapat dikonfirmasi, atau jalur pendaftaran lewat agregator/perantara; butuh verifikasi |
| LOW | Employer teridentifikasi dan kanal pendaftaran sesuai domain/platform resmi, tanpa permintaan uang/data sensitif awal |

Aturan: (1) dua anotator terpisah, hitung Cohen's kappa (target ≥0.7), selisih diadjudikasi; (2) catat `gold_evidence_url`;
(3) kampanye yang sama (domain/akun/nomor sama) memakai `campaign_group` yang sama dan tidak boleh terpisah antara dev/test;
(4) UMKM, Gmail, WA pribadi, gaji tinggi, shortlink **bukan** alasan HIGH jika tidak ada bukti lain;
(5) poster yang employer-nya valid tapi memakai shortlink (mis. Pakuwon, Dexa) dilabeli LOW/MEDIUM, bukan HIGH — inilah yang diuji sebagai false positive.
