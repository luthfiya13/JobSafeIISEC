"""Menghasilkan data/gold_regression_cases.csv — kasus SINTETIK buatan tangan untuk regression test aturan.
BUKAN data empiris: jangan dipakai untuk melaporkan akurasi di paper."""
import csv
C=[
# id, expected, tag, text
("S01","HIGH","scam_fee","LOWONGAN PT Maju Jaya. Dibutuhkan 20 staff admin, gaji 8 juta. Wajib transfer biaya pendaftaran Rp 250.000 untuk seragam. Hubungi WA 081234567890. Kuota terbatas hanya 10 orang!"),
("S02","HIGH","scam_fee","Lolos seleksi tahap 1. Untuk mengamankan slot kerja Anda harap membayar uang administrasi Rp 300.000 ke rekening BCA berikut, setelah itu langsung interview."),
("S03","HIGH","scam_task","Kerja sampingan dari rumah, tugas harian like & subscribe, komisi Rp 50.000 per tugas. Wajib top up saldo awal 500rb, modal akan dikembalikan beserta komisi."),
("S04","HIGH","scam_task","Part time santai cukup like video TikTok 100rb/hari. Deposit modal 200rb dulu untuk aktivasi akun tugas. Pasti profit."),
("S05","HIGH","scam_cambodia","Loker Kamboja customer service online gaji $2000 tanpa pengalaman tanpa bahasa Inggris. Proses legal jalur khusus, kirim foto KTP via WA 0812345678."),
("S06","HIGH","scam_cambodia","Dibutuhkan CS online Kamboja gaji $2000, tanpa pengalaman. Berangkat cepat, jalur khusus, kirim foto KTP dan paspor ke WA 0812345678"),
("S07","HIGH","scam_overseas","Kerja Jepang gaji 30 juta, wajib beli tiket lewat agen kami, biaya keberangkatan dipotong dari gaji, tanpa izin P3MI, dana talangan 90%."),
("S08","HIGH","scam_impersonation","LOWONGAN BUMN PT Pertamina 2026 admin teller. Daftar di goletskerja.com atau scan QR. Kirim foto KTP dan nomor rekening sekarang juga, kuota terbatas."),
("S09","HIGH","scam_impersonation","Rekrutmen Randstad Australia pekerja luar negeri, gaji 40-60 juta, dana talangan 90%. Kirim CV ke achmadrandy2018@gmail.com atau WA +62 813-6092-9771."),
("S10","HIGH","scam_credential","Verifikasi akun rekrutmen: mohon kirimkan kode OTP yang masuk ke HP Anda agar data pendaftaran tersimpan."),
("S11","HIGH","scam_fee","Neo Travels Jobs in Thailand cleaning construction. Advance payment 30,000 INR non-refundable. Hubungi +91 8729049115. Fly in just 10 days, tanpa bahasa."),
("S12","HIGH","scam_data","Hero Media Online (Solo) butuh staff content. Pendaftaran awal wajib kirim foto KTP via WhatsApp 087721207077 sebelum interview."),
("S13","HIGH","scam_task","Admin online: cukup like dan review produk, komisi dibayar per tugas. Setor modal awal Rp 100.000 untuk membuka paket tugas."),
("S14","HIGH","scam_fee","Kami menerima karyawan pabrik. Siapkan uang administrasi Rp 150.000 dan bawa saat tes kesehatan agar diterima."),
("M01","MEDIUM","impersonation_only","Rekrutmen BNI Bina BNI Teller 2026. Daftar di goletskerja.com. Syarat S1 semua jurusan, lokasi seluruh Indonesia."),
("M02","MEDIUM","impersonation_only","Lowongan Kementerian PUPR teknis sipil dan admin. Daftar melalui link di bio akun updateinfoloker.id"),
("M03","MEDIUM","overseas_single","Dibutuhkan pekerja kebun di Australia, lulusan SMA, penempatan tidak jelas, hubungi WA admin."),
("M04","MEDIUM","pressure_only","Lowongan admin gudang PT Sentosa, syarat SMA, lokasi Bekasi. Segera daftar, kuota terbatas, klik link pendaftaran di bio."),
("L01","LOW","umkm_gmail","Dibutuhkan Kasir Toko Armindo Magelang. Jl. Soekarno Hatta No.2. Syarat: min SMA, jujur, pengalaman 1 tahun. Kirim lamaran ke armindomagelang21@gmail.com atau WA 082227187988. Gaji sesuai UMK."),
("L02","LOW","umkm_wa","Warung Soto Hj. Hesti butuh waiters dan kitchen helper, lokasi Depok, syarat SMP, gaji UMK. Kirim lamaran via WA HRD 0812-2937-7625. Tidak dipungut biaya."),
("L03","LOW","legit_free","Job Title: Staff GA. Company: PT Tritunggal Swarna. Location: Paseh. Experience: 1-3 years. Requirements: Microsoft Office. Responsibilities: Mengelola perawatan gedung. Pendaftaran gratis, tidak dipungut biaya apa pun. Waspada penipuan."),
("L04","LOW","bank_mobile_banking","Job Title: Customer Service Bank. Company: PT Bank Rakyat Maju. Requirements: memahami produk mobile banking dan PIN kartu. Responsibilities: melayani nasabah. Lokasi Jakarta. Gaji sesuai UMK."),
("L05","LOW","legit_warning","Lowongan Staff Admin PT Sinar Abadi. Kualifikasi: S1, 1 tahun pengalaman. Lokasi Bandung. Waspada penipuan! Ada akun palsu mengatasnamakan perusahaan kami. Kami tidak pernah meminta biaya apa pun. Info resmi hanya di karir.sinarabadi.co.id"),
("L06","LOW","word_bri_fabric","Lowongan PT Fabrikasi Maju (brief). Kualifikasi D3, lokasi Cikarang, tanggung jawab produksi dan fabrication. Daftar di www.fabrikasimaju.co.id/karir."),
("L07","LOW","jl_address","Rekrutmen BNI Teller. Lokasi Jl.Sudirman No.1 Jakarta. Syarat S1. Daftar di bni.co.id/karir"),
("L08","LOW","doc_list","Admin Gudang PT Alpha Logistik, lokasi Cikarang. Berkas lamaran: surat lamaran, CV, fotokopi KTP, fotokopi KK, ijazah. Kirim ke hrd@alphalogistik.co.id. Gaji UMK."),
("L09","LOW","high_salary_legit","Job Title: Senior Software Engineer. Company: PT Teknologi Nusantara. Gaji Rp 25 juta per bulan. Requirements: 5 tahun pengalaman Java, Spring. Responsibilities: membangun layanan backend. Lokasi Jakarta Selatan."),
("L10","LOW","overseas_legit","Penempatan resmi P3MI berizin: pekerja perawat lansia di Jepang program G to G. Syarat D3 keperawatan, lulus JLPT N4. Proses melalui KP2MI, tanpa biaya penempatan sesuai ketentuan. Info lengkap di website resmi."),
("L11","LOW","travel_provided","Operator produksi PT Kao Indonesia, lokasi Karawang. Fasilitas mess dan tiket pulang tahunan disediakan perusahaan. Syarat SMK, shift. Kirim lamaran ke recruitment@kao.co.id"),
("L12","LOW","shortlink_company","Dexa Group Medical Representative Yogyakarta. Syarat D3 Farmasi, SIM C. Lokasi Yogyakarta. Daftar lewat bit.ly/apply-DXG. Dexa tidak memungut biaya apa pun."),
("L13","LOW","normal_deadline","Staf HR PT Gamma Sejahtera, lokasi Surabaya. Syarat S1 Psikologi, pengalaman 2 tahun. Lamaran paling lambat 30 Oktober 2026 ke karir@gammasejahtera.co.id"),
("L14","LOW","startup","Startup fintech di Bandung mencari UI designer. Syarat portfolio Figma, pengalaman 1 tahun. Lokasi hybrid. Kirim portfolio via email ke hello@startupku.id"),
]
with open("data/gold_regression_cases.csv","w",newline="",encoding="utf-8-sig") as f:
    w=csv.writer(f); w.writerow(["case_id","expected_level","tag","text","provenance"])
    for r in C: w.writerow(list(r)+["SYNTHETIC_HAND_WRITTEN"])
print(len(C))
