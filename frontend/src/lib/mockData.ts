export const PRESET_JOBS = [
  {
    id: "sample-high-task",
    title: "Skema Misi Like Video & Top-Up (Risiko Tinggi)",
    badge: "Contoh Risiko Tinggi",
    badgeColor: "bg-red-50 text-red-700 border-red-200",
    text: `Dicari Admin Online Freelance!
Pekerjaan sangat santai, cukup punya HP dan kuota internet.
Tugas Anda: Like video TikTok, subscribe YouTube, dan beri rating ulasan toko online.
Penghasilan: Rp500.000 - Rp1.000.000/hari, langsung cair ke rekening atau DANA setiap hari!
Syarat:
- Tanpa syarat ijazah, tanpa pengalaman kerja, siapa saja bisa bergabung.
- Kuota sangat terbatas hanya untuk 10 pendaftar pertama hari ini!
- Untuk aktivasi akun tugas dan jaminan modul kerja, calon peserta diwajibkan transfer deposit awal sebesar Rp250.000. Uang deposit akan dikembalikan bersama gaji hari pertama.
Hubungi admin sekarang juga via WhatsApp pribadi: wa.me/6281234567890 (Segera chat, kesempatan terakhir sebelum kuota ditutup!).`
  },
  {
    id: "sample-high-travel",
    title: "Surat Panggilan Rekrutmen via Travel Fiktif (Risiko Tinggi)",
    badge: "Contoh Risiko Tinggi",
    badgeColor: "bg-red-50 text-red-700 border-red-200",
    text: `SURAT PANGGILAN TES SELEKSI TAHAP AKHIR
PT ENERGI NUSANTARA PERSADA TBK (PERSERO)
Selamat, berkas lamaran Anda telah lolos seleksi administratif. Anda diundang untuk mengikuti wawancara akhir dan medical check-up di Surabaya.

Ketentuan Pelaksanaan:
1. Panitia rekrutmen bekerjasama dengan agen travel resmi panitia yaitu CV Bintang Angkasa Tour & Travel untuk reservasi tiket pesawat dan hotel penginapan.
2. Demi keseragaman jadwal, seluruh biaya akomodasi dan tiket pesawat wajib dipesan melalui agen travel yang ditunjuk.
3. Seluruh biaya perjalanan sebesar Rp1.850.000 akan diganti (reimburse) penuh oleh pihak perusahaan setibanya peserta di lokasi tes.
4. Segera lakukan konfirmasi reservasi tiket ke pihak travel sebelum pukul 17.00 WIB hari ini.`
  },
  {
    id: "sample-medium-remote",
    title: "Data Entry Remote Minta KTP & Kontak WA (Risiko Sedang)",
    badge: "Contoh Risiko Sedang",
    badgeColor: "bg-amber-50 text-amber-700 border-amber-200",
    text: `Lowongan Pekerjaan: Data Entry & Staff Pengetikan Dokumen WFH (Work From Home).
Perusahaan multinasional terkemuka membuka kesempatan kerja paruh waktu untuk mahasiswa dan fresh graduate.
Gaji: Rp3.500.000/bulan + bonus kinerja.
Persyaratan:
- Mampu mengetik rapi
- Memiliki laptop / smartphone
- Kirimkan foto KTP depan belakang, foto selfie memegang KTP, dan foto buku tabungan nomor rekening untuk proses verifikasi data penggajian awal.
Kirimkan kelengkapan berkas lamaran hanya melalui chat WhatsApp HRD di wa.me/628987654321.`
  },
  {
    id: "sample-low-legit",
    title: "Lowongan Kerja Profesional di Perusahaan Resmi (Risiko Rendah)",
    badge: "Contoh Risiko Rendah",
    badgeColor: "bg-green-50 text-green-700 border-green-200",
    text: `Lowongan Kerja: Junior Software Engineer (React / Next.js)
PT Solusi Teknologi Digital (Jakarta Selatan)

Tentang Kami:
PT Solusi Teknologi Digital adalah perusahaan teknologi penyedia solusi cloud computing berizin resmi Kemenkumham (SK No. AHU-0012345.AH.01.01). Kunjungi profil resmi kami di https://solusiteknologi.co.id.

Tanggung Jawab:
- Mengembangkan antarmuka web responsif menggunakan React dan Next.js.
- Berkolaborasi dengan tim backend dalam integrasi RESTful API.
- Menulis unit testing dan dokumentasi kode teknis.

Kualifikasi:
- Lulusan S1/D3 Ilmu Komputer, Sistem Informasi, atau bidang terkait (Fresh graduate dipersilakan).
- Memahami dasar JavaScript/TypeScript, HTML5, dan CSS3/Tailwind.
- Memiliki portofolio proyek atau akun GitHub yang dapat ditinjau.

Proses Rekrutmen:
1. Seleksi Administrasi & Portofolio
2. Tes Teknis / Coding Challenge Online
3. Wawancara Pengguna & HR

Pemberitahuan Resmi:
Proses rekrutmen ini TIDAK MEMUNGUT BIAYA APAPUN. Perusahaan tidak pernah meminta uang pendaftaran, deposit, maupun pemesanan tiket travel. Kirimkan CV dan portofolio Anda melalui email resmi: recruitment@solusiteknologi.co.id dengan subjek [Lamaran - Junior SE - Nama Anda].`
  }
];

export const STATIC_INDICATORS = [
  {
    code: "R1",
    name: "Biaya di Awal",
    weight: 15,
    category: "Keuangan",
    description: "Permintaan biaya pendaftaran, deposit, pelatihan, materi kerja, atau pembayaran apa pun sebelum resmi bekerja.",
    why_important: "Perusahaan legal menanggung seluruh biaya rekrutmen. Permintaan uang di awal proses lamaran adalah indikator paling umum dari risiko penipuan kerja."
  },
  {
    code: "R2",
    name: "Imbalan Tidak Wajar",
    weight: 10,
    category: "Kompensasi",
    description: "Penawaran penghasilan, komisi, atau gaji harian yang sangat tinggi dan tidak rasional dibandingkan beban kerja atau kualifikasi yang diminta.",
    why_important: "Penawaran gaji fantastis dengan kualifikasi minimal sering dimanfaatkan untuk memikat korban agar tidak berpikir kritis terhadap risiko yang ada."
  },
  {
    code: "R3",
    name: "Permintaan Dokumen Sensitif",
    weight: 15,
    category: "Privasi & Legalitas",
    description: "Permintaan foto KTP, foto selfie dengan KTP, nomor rekening, KK, atau informasi sensitif sebelum ada proses wawancara/seleksi yang sah.",
    why_important: "Data pribadi sensitif seperti foto KTP + selfie sangat rentan disalahgunakan untuk pinjaman online ilegal atau pencurian identitas digital."
  },
  {
    code: "R4",
    name: "Identitas Perusahaan Tidak Jelas",
    weight: 10,
    category: "Profil Perusahaan",
    description: "Identitas perusahaan, alamat kantor fisik, atau kontak resmi tidak jelas, anonim, atau menggunakan email/domain gratisan tanpa domain perusahaan resmi.",
    why_important: "Perusahaan bonafide memiliki legalitas, alamat kantor fisik yang dapat diverifikasi di peta/Kemenkumham, serta saluran email korporat resmi."
  },
  {
    code: "R5",
    name: "Deskripsi Pekerjaan Tidak Jelas",
    weight: 10,
    category: "Uraian Pekerjaan",
    description: "Deskripsi pekerjaan ambigu, serba bisa, tidak terstruktur, tidak menjelaskan KPI, alur kerja, atau tanggung jawab secara spesifik.",
    why_important: "Lowongan profesional merinci kualifikasi, deskripsi tugas pokok, dan kriteria keahlian. Deskripsi yang terlalu samar sering menyembunyikan skema terlarang."
  },
  {
    code: "R6",
    name: "Skema Tugas Berantai",
    weight: 15,
    category: "Modus Operasional",
    description: "Modus pekerjaan berbasis misi berantai seperti like postingan media sosial, subscribe channel, rating e-commerce, atau top-up saldo bertingkat.",
    why_important: "Pelaku biasanya mencairkan komisi kecil di awal lalu meminta top-up deposit besar yang akhirnya tidak dapat ditarik kembali oleh korban."
  },
  {
    code: "R7",
    name: "Perjalanan/Akomodasi Wajib",
    weight: 10,
    category: "Logistik & Travel",
    description: "Panggilan tes seleksi di kota lain dengan kewajiban memesan tiket pesawat, hotel, atau akomodasi melalui biro travel tertentu yang ditunjuk.",
    why_important: "Modus klasik rekrutmen fiktif sering memalsukan surat panggilan resmi, lalu mewajibkan peserta memesan akomodasi lewat agen travel rekanan palsu."
  },
  {
    code: "R8",
    name: "Kanal Komunikasi Tidak Resmi",
    weight: 5,
    category: "Saluran Kontak",
    description: "Seluruh proses seleksi dan komunikasi hanya dilakukan melalui akun pribadi WhatsApp atau Telegram tanpa identitas organisasi yang terverifikasi.",
    why_important: "Aplikasi pesan instan pribadi menyulitkan pelacakan identitas perekrut dan sering dimanfaatkan karena akun dapat dihapus sewaktu-waktu tanpa jejak."
  },
  {
    code: "R9",
    name: "Tawaran Kerja Luar Negeri Berisiko",
    weight: 5,
    category: "Ketenagakerjaan Migran",
    description: "Tawaran pekerjaan di luar negeri tanpa kejelasan izin resmi P3MI, visa kerja resmi, atau verifikasi BP2MI.",
    why_important: "Banyak penipuan kerja luar negeri berujung pada tindak pidana perdagangan orang (TPPO) atau operator online scam di perbatasan dengan visa turis."
  },
  {
    code: "R10",
    name: "Urgensi Palsu",
    weight: 5,
    category: "Teknik Persuasi",
    description: "Penggunaan frasa tekanan batas waktu ekstrim ('kuota terbatas', 'harus transfer dalam 1 jam', 'kesempatan terakhir') untuk memicu kepanikan.",
    why_important: "Tekanan waktu mendesak dirancang oleh penipu untuk mematikan rasionalitas calon korban agar segera mengambil keputusan impulsif sebelum sempat memverifikasi."
  }
];
