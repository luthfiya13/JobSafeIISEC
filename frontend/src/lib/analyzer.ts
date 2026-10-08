export interface IndicatorConfig {
  code: string;
  name: string;
  weight: number;
  hard_flag: boolean;
  is_active: boolean;
  category: string;
  description: string;
  why_important: string;
  keywords: string[];
  patterns: RegExp[];
}

export const DEFAULT_INDICATORS: IndicatorConfig[] = [
  {
    code: "R1",
    name: "Biaya di Awal",
    weight: 15,
    hard_flag: true,
    is_active: true,
    category: "Keuangan",
    description: "Permintaan biaya pendaftaran, deposit, pelatihan, materi kerja, atau pembayaran apa pun sebelum resmi bekerja.",
    why_important: "Perusahaan legal dan beritikad baik umumnya menanggung seluruh biaya rekrutmen. Permintaan uang di awal proses lamaran adalah indikator paling umum dari risiko penipuan kerja.",
    keywords: [
      "biaya pendaftaran", "uang pendaftaran", "biaya pelatihan", "uang jaminan", "deposit", 
      "biaya awal pendaftaran", "biaya awal keberangkatan", "biaya pengurusan visa",
      "biaya seragam", "biaya materai", "biaya administrasi", "transfer dulu", "bayar dulu",
      "biaya modul", "biaya kartu member", "biaya tes", "biaya medical", "reimburse tiket",
      "uang pangkal", "biaya psikotes", "biaya proses", "biaya id card"
    ],
    patterns: [
      /(?:biaya|uang|dana)\s+(?:awal\s+)?(?:pendaftaran|registrasi|administrasi|keberangkatan|pengurusan\s+(?:visa|dokumen))[^.!?\n]{0,100}(?:rp\.?\s*[\d.,]+|\d[\d.,]*\s*(?:rb|ribu|juta))/i,
      /(?:biaya|uang|dana)\s*(?:pendaftaran|registrasi|admin|administrasi|pelatihan|seragam|materai|deposit|jaminan|tes|training)/i,
      /(?:wajib|harus|diminta)\s*(?:membayar|transfer|deposit|topup|top\s*up)\s*(?:sebesar|sejumlah|rp|\d+)/i,
      /(?:deposit|jaminan)\s*(?:awal|sebesar|rp|\d+)/i,
      /(?:reimburse|diganti|penggantian)\s*(?:setelah|nanti|setibanya|oleh perusahaan)/i,
      /(?:transfer|kirim)\s*(?:biaya|uang|dana)\s*(?:ke|melalui|via)\s*(?:rekening|dana|ovo|gopay)/i
    ]
  },
  {
    code: "R2",
    name: "Imbalan Tidak Wajar",
    weight: 10,
    hard_flag: false,
    is_active: true,
    category: "Kompensasi",
    description: "Penawaran penghasilan, komisi, atau gaji harian yang sangat tinggi dan tidak rasional dibandingkan beban kerja atau kualifikasi yang diminta.",
    why_important: "Penawaran gaji fantastis dengan kualifikasi minimal (tanpa pengalaman/hanya perlu HP) sering dimanfaatkan untuk memikat korban agar tidak berpikir kritis terhadap risiko yang ada.",
    keywords: [
      "gaji 500rb per hari", "gaji 1jt per hari", "500.000 per hari", "1.000.000/hari", "penghasilan harian",
      "cukup punya hp", "cuma like", "hanya modal hp", "profit instan", "komisi instan", "cuan cepat",
      "penghasilan tak terbatas", "hanya 15 menit", "kerja santai gaji jutaan", "penghasilan 5-10 juta/minggu"
    ],
    patterns: [
      /(?:penghasilan|gaji|komisi|upah)\s*(?:rp\s*)?(?:[3-9]\d{2}\.?\d{3}|[1-9]\.?\d{6})\s*(?:per\s*hari|\/hari|harian|tiap\s*hari)/i,
      /(?:kerja|tugas)\s*(?:santai|mudah|ringan)\s*(?:gaji|penghasilan|dapat)\s*(?:jutaan|besar|melimpah)/i,
      /(?:hanya|cukup)\s*(?:modal\s*hp|punya\s*hp|rebahan|like\s*video)\s*(?:dapat|menghasilkan|hasilkan)\s*(?:rp|juta|\d+)/i,
      /(?:profit|keuntungan)\s*(?:harian|langsung|cair\s*tiap\s*hari|instan)\s*(?:rp|\d+)/i
    ]
  },
  {
    code: "R3",
    name: "Permintaan Dokumen Sensitif",
    weight: 8,
    hard_flag: false,
    is_active: true,
    category: "Privasi & Legalitas",
    description: "Permintaan foto KTP, foto selfie dengan KTP, nomor rekening, KK, atau informasi sensitif sebelum ada proses wawancara/seleksi yang sah.",
    why_important: "Data pribadi sensitif seperti foto KTP + selfie sangat rentan disalahgunakan untuk pinjaman online ilegal, pendaftaran rekening penampung penipuan, atau pencurian identitas digital.",
    keywords: [
      "foto ktp", "selfie ktp", "foto bersama ktp", "nomor kartu keluarga", "buku tabungan",
      "nomor rekening", "otp", "pin rekening", "kirim ktp ke whatsapp", "upload ktp", "foto identitas",
      "data login", "password rekening", "selfie pegang ktp"
    ],
    patterns: [
      /(?:kirim|unggah|upload|lampirkan|serahkan|wajib\s*mengirim)\s*(?:foto\s*)?(?:ktp|e-ktp|kk|kartu\s*keluarga|nomor\s*rekening)/i,
      /(?:kirim|unggah|upload|lampirkan|sertakan)\s*(?:foto\s*ktp|selfie\s*(?:dengan|memegang|pegang)?\s*ktp|foto\s*buku\s*tabungan)/i,
      /(?:foto|scan)\s*(?:ktp|e-ktp|kartu\s*keluarga|kk|buku\s*rekening)\s*(?:asli|depan\s*belakang)/i,
      /(?:nomor|no)\s*(?:rekening|cvv|otp|pin)\s*(?:untuk\s*verifikasi|pendaftaran|gaji)/i,
      /selfie\s*(?:pegang|bersama|sambil\s*memegang)\s*ktp/i
    ]
  },
  {
    code: "R4",
    name: "Identitas Perusahaan Tidak Jelas",
    weight: 10,
    hard_flag: false,
    is_active: true,
    category: "Profil Perusahaan",
    description: "Email perekrut menggunakan domain publik/gratis atau identitas email anonim, bukan alamat domain resmi perusahaan.",
    why_important: "Perusahaan bonafide memiliki legalitas, alamat kantor fisik yang dapat diverifikasi di peta/Kemenkumham, serta saluran email korporat resmi dengan domain perusahaan.",
    keywords: [
      "@gmail.com", "@yahoo.com", "@hotmail.com", "@outlook.com", "@ymail.com"
    ],
    patterns: [
      /(?:email|kirim\s*cv\s*ke)\s*:\s*[a-zA-Z0-9._%+-]+@(?:gmail|yahoo|hotmail|outlook|ymail)\.com/i,
      /(?:email|alamat\s*email)\s*(?:anonim|pribadi|tidak\s*resmi|tidak\s*terverifikasi)/i
    ]
  },
  {
    code: "R5",
    name: "Deskripsi Pekerjaan Tidak Jelas",
    weight: 7,
    hard_flag: false,
    is_active: true,
    category: "Uraian Pekerjaan",
    description: "Deskripsi pekerjaan ambigu, serba bisa, tidak terstruktur, tidak menjelaskan KPI, alur kerja, atau tanggung jawab secara spesifik.",
    why_important: "Lowongan profesional merinci kualifikasi, deskripsi tugas pokok harian, dan kriteria keahlian. Deskripsi yang terlalu samar sering menyembunyikan skema penipuan atau tugas terlarang.",
    keywords: [
      "tugas apa saja", "kerja gampang", "hanya ikuti arahan", "cuma copy paste", "input data santai",
      "tugas fleksibel apa saja", "siapa saja bisa", "tidak butuh pengalaman sama sekali", "tanpa kualifikasi"
    ],
    patterns: [
      /(?:pekerjaan|tugas)\s*(?:sangat\s*mudah|hanya\s*ikuti\s*instruksi|cukup\s*salin\s*tempel|cuma\s*copy\s*paste)/i,
      /(?:tanpa\s*syarat|tanpa\s*keahlian|tidak\s*perlu\s*skill|semua\s*bisa\s*diterima)/i,
      /(?:deskripsi\s*kerja|jobdesk)\s*(?:fleksibel|bebas|apa\s*saja|santai)/i
    ]
  },
  {
    code: "R6",
    name: "Skema Tugas Berantai",
    weight: 15,
    hard_flag: true,
    is_active: true,
    category: "Modus Operasional",
    description: "Modus pekerjaan berbasis misi berantai seperti like postingan media sosial, subscribe channel, rating e-commerce, atau top-up saldo bertingkat.",
    why_important: "Modus 'freelance like & subscribe' atau tugas e-commerce bertingkat adalah salah satu tren scam paling marak. Pelaku biasanya mencairkan komisi kecil di awal lalu meminta top-up besar yang akhirnya tidak dapat dicairkan.",
    keywords: [
      "like dan subscribe", "like video tiktok", "subscribe youtube", "follow ig", "tugas pesanan",
      "rating toko", "top up saldo misi", "tugas pesanan berbayar", "pesanan fiktif", "komisi bertingkat",
      "misi ke-1", "misi level", "selesaikan tugas", "screeshot bukti like"
    ],
    patterns: [
      /(?:tugas|misi)\s*(?:bertingkat|level\s*\d+|top\s*up|deposit\s*saldo|pesanan\s*fiktif)/i,
      /(?:screenshot|ss)\s*bukti\s*(?:like|follow|subscribe|tugas)\s*(?:lalu\s*cair|dapat\s*komisi)/i,
      /(?:selesaikan|jalankan)\s*(?:tugas|misi)\s*(?:untuk\s*menaikkan\s*komisi|ambil\s*bonus)/i
    ]
  },
  {
    code: "R7",
    name: "Perjalanan/Akomodasi Wajib",
    weight: 10,
    hard_flag: true,
    is_active: true,
    category: "Logistik & Travel",
    description: "Panggilan tes seleksi di kota lain dengan kewajiban memesan tiket pesawat, hotel, atau akomodasi melalui biro travel / pihak tertentu yang ditunjuk.",
    why_important: "Modus klasik rekrutmen BUMN atau migas fiktif sering memalsukan surat panggilan resmi bertanda tangan pejabat, lalu mewajibkan peserta memesan akomodasi lewat 'agen travel' fiktif dengan janji palsu penggantian (reimbursement).",
    keywords: [
      "biro travel", "agen travel yang ditunjuk", "reservasi tiket", "pemesanan tiket hotel",
      "biaya akomodasi", "surat panggilan tes", "penggantian tiket di lokasi", "reimbursement tiket",
      "panitia rekrutmen bekerjasama dengan travel"
    ],
    patterns: [
      /(?:agen|biro|pihak)\s*travel\s*(?:yang\s*ditunjuk|rekanan|resmi\s*panitia)/i,
      /(?:tiket|akomodasi|hotel)\s*(?:wajib\s*dipesan|harus\s*melalui|hanya\s*dapat\s*dipesan)/i,
      /(?:biaya\s*perjalanan|tiket)\s*(?:akan\s*diganti|direimburse|ditanggung\s*penuh\s*setelah\s*tiba)/i
    ]
  },
  {
    code: "R8",
    name: "Kanal Komunikasi Tidak Resmi",
    weight: 10,
    hard_flag: false,
    is_active: true,
    category: "Saluran Kontak",
    description: "Seluruh proses seleksi dan komunikasi hanya dilakukan melalui akun pribadi WhatsApp atau Telegram tanpa identitas organisasi yang terverifikasi.",
    why_important: "Aplikasi pesan instan pribadi menyulitkan pelacakan identitas perekrut dan sering dimanfaatkan karena akun dapat dihapus sewaktu-waktu tanpa jejak rekam jejak formal.",
    keywords: [
      "hubungi wa", "chat wa pribadi", "gabung grup telegram", "klik link telegram",
      "admin wa", "hanya lewat wa", "wa.me/", "t.me/", "kontak telegram"
    ],
    patterns: [
      /(?:whatsapp|wa|telegram)\s*(?:pribadi|personal)|(?:hanya|cuma)\s*(?:melalui|lewat|via)\s*(?:whatsapp|wa|telegram)/i,
      /(?:wa\.me\/\d+|t\.me\/[a-zA-Z0-9_]+)/i,
      /(?:hubungi|chat|kontak)\s*(?:admin|hrd|recruiter)\s*(?:hanya\s*melalui|via|ke)\s*(?:whatsapp|wa|telegram)/i,
      /(?:gabung|masuk)\s*(?:grup|channel)\s*telegram\s*(?:untuk\s*penjelasan|tugas|kerja)/i
    ]
  },
  {
    code: "R9",
    name: "Tawaran Kerja Luar Negeri Berisiko",
    weight: 15,
    hard_flag: true,
    is_active: true,
    category: "Ketenagakerjaan Migran",
    description: "Tawaran pekerjaan di luar negeri (seperti Kamboja, Myanmar, Filipina, dll.) tanpa kejelasan izin resmi P3MI, visa kerja resmi, atau verifikasi BP2MI.",
    why_important: "Banyak penipuan kerja luar negeri berujung pada tindak pidana perdagangan orang (TPPO) atau operator online scam di perbatasan, dengan visa turis bukan visa kerja resmi.",
    keywords: [
      "kerja kamboja", "tujuan kamboja", "kamboja", "kerja myanmar", "kerja luar negeri tanpa bahasa", "visa turis dulu",
      "berangkat dulu visa menyusul", "operator scam", "customer service kamboja", "gaji dollar luar negeri"
    ],
    patterns: [
      /(?:tujuan|penempatan|lokasi\s+kerja)\s*:?\s*(?:di\s+|ke\s+)?(?:kamboja|cambodia|myanmar|laos|filipina)/i,
      /(?:kerja|lowongan)\s*(?:di|ke)\s*(?:kamboja|myanmar|laos|filipina|cambodia)\s*(?:gaji\s*dollar|tanpa\s*syarat|cs|admin)/i,
      /(?:visa\s*kunjungan|visa\s*turis)\s*(?:dulu|nanti\s*diubah|bisa\s*bekerja)/i,
      /(?:tanpa\s*izin\s*bp2mi|tanpa\s*p3mi|berangkat\s*cepat\s*tanpa\s*birokrasi)/i
    ]
  },
  {
    code: "R10",
    name: "Urgensi Palsu",
    weight: 5,
    hard_flag: false,
    is_active: true,
    category: "Teknik Persuasi",
    description: "Penggunaan frasa tekanan batas waktu ekstrim ('kuota terbatas', 'harus daftar/transfer dalam 1 jam', 'kesempatan terakhir') untuk memicu kepanikan (FOMO).",
    why_important: "Tekanan waktu mendesak dirancang oleh penipu untuk mematikan rasionalitas dan analisis kritis calon korban agar segera mengambil keputusan impulsif sebelum sempat memverifikasi.",
    keywords: [
      "kuota terbatas", "hanya untuk 5 orang pertama", "segera daftar sebelum ditutup", "dalam 1 jam",
      "kesempatan terakhir", "slot tersisa sedikit", "sekarang juga", "batas transfer hari ini"
    ],
    patterns: [
      /(?:kuota|slot)\s*(?:sangat\s*terbatas|tersisa\s*(?:hanya\s*)?\d+|tinggal\s*\d+)/i,
      /(?:hanya\s*hari\s*ini|dalam\s*waktu\s*\d+\s*(?:menit|jam)|segera\s*sebelum\s*kehabisan)/i,
      /(?:kesempatan\s*terakhir|jangan\s*sampai\s*ketinggalan|buru\s*buru\s*daftar)/i
    ]
  }
];

// Keep the browser fallback on the same probability scale as the API engine
// (jobsafe_config.json). UI indicator weights are display metadata, not risk
// probabilities, so summing them made browser and server scores disagree.
const RISK_BASE_RATES: Record<string, number> = {
  R1: 0.85, R2: 0.3, R3: 0.65, R4: 0.65, R5: 0.3,
  R6: 0.88, R7: 0.55, R8: 0.25, R9: 0.8, R10: 0.4
};

export const VERIFICATION_STEPS = [
  {
    id: "v1",
    title: "Periksa apakah perusahaan benar-benar memiliki website resmi",
    desc: "Cari situs web independen perusahaan dan pastikan domain terdaftar secara profesional, bukan blog gratisan atau halaman sosial media tanpa bukti hukum."
  },
  {
    id: "v2",
    title: "Periksa apakah domain email sesuai dengan nama perusahaan",
    desc: "Perusahaan profesional menggunakan email berdomain khusus (contoh: hr@namaperusahaan.co.id), bukan akun gratis umum seperti @gmail.com atau @yahoo.com."
  },
  {
    id: "v3",
    title: "Cari informasi perusahaan melalui sumber resmi",
    desc: "Cek keabsahan PT/CV di database resmi Ditjen AHU Kemenkumham, profil LinkedIn perusahaan, atau portal karier terakreditasi."
  },
  {
    id: "v4",
    title: "Pastikan kontak perekrut dapat diverifikasi",
    desc: "Gunakan aplikasi identifikasi nomor telepon (seperti Getcontact) untuk memeriksa reputasi nomor kontak recruiter dan membaca tag dari pengguna lain."
  },
  {
    id: "v5",
    title: "Jangan membayar biaya apa pun yang tidak jelas",
    desc: "Ingat prinsip utama: Proses rekrutmen yang sah TIDAK PERNAH memungut uang pendaftaran, biaya seragam, materi pelatihan, atau deposit dari kandidat."
  },
  {
    id: "v6",
    title: "Jangan memberikan dokumen sensitif sebelum proses yang wajar",
    desc: "Hindari mengirim foto KTP, selfie dengan KTP, atau informasi kartu/rekening bank sebelum Anda dinyatakan diterima resmi dengan kontrak kerja tertulis."
  },
  {
    id: "v7",
    title: "Periksa informasi izin resmi untuk tawaran kerja luar negeri",
    desc: "Pastikan agen penyalur tercatat resmi di Kementerian Ketenagakerjaan (Kemnaker) atau SISKOP2MI / BP2MI dengan jenis visa kerja yang legal."
  },
  {
    id: "v8",
    title: "Jangan terburu-buru karena tekanan waktu",
    desc: "Penipu sering menciptakan kepanikan ('kuota terbatas', 'harus transfer hari ini'). Ambil jeda waktu untuk berdiskusi dengan keluarga atau rekan terpercaya."
  }
];

export function analyzeJobText(text: string) {
  const cleaned = text.trim();
  if (cleaned.length < 15) {
    throw new Error("Teks lowongan terlalu pendek. Masukkan minimal 15 karakter untuk analisis.");
  }

  const lower = cleaned.toLowerCase();
  let totalScore = 0;
  let criticalFloor = 0;
  let combinedRiskProbability = 0;
  let highCount = 0;
  let attentionCount = 0;
  const detectedNames: string[] = [];

  const detectedIndicators = DEFAULT_INDICATORS.map((ind) => {
    const matches: string[] = [];
    let evidence: string | null = null;

    // Check regex
    for (const pattern of ind.patterns) {
      const match = pattern.exec(cleaned);
      if (match) {
        const contextBefore = cleaned.slice(Math.max(0, match.index - 42), match.index);
        if (/\b(?:tidak|tanpa|bebas|dilarang|jangan)\b[^.!?\n]{0,42}$/i.test(contextBefore)) {
          continue;
        }
        matches.push(match[0]);
        if (!evidence) {
          const start = Math.max(0, match.index - 50);
          const end = Math.min(cleaned.length, match.index + match[0].length + 50);
          const snippet = cleaned.substring(start, end).replace(/\s+/g, " ").trim();
          evidence = `...${snippet}...`;
        }
      }
    }

    // Check keywords if no regex matches
    if (matches.length === 0) {
      for (const kw of ind.keywords) {
        const idx = lower.indexOf(kw.toLowerCase());
        if (idx !== -1) {
          const contextBefore = cleaned.slice(Math.max(0, idx - 42), idx);
          if (/\b(?:tidak|tanpa|bebas|dilarang|jangan)\b[^.!?\n]{0,42}$/i.test(contextBefore)) {
            continue;
          }
          matches.push(kw);
          if (!evidence) {
            const start = Math.max(0, idx - 50);
            const end = Math.min(cleaned.length, idx + kw.length + 50);
            const snippet = cleaned.substring(start, end).replace(/\s+/g, " ").trim();
            evidence = `...${snippet}...`;
          }
        }
      }
    }

    const weight = ind.weight;
    let status: "RISIKO_TINGGI" | "PERLU_PERHATIAN" | "TIDAK_TERDETEKSI" = "TIDAK_TERDETEKSI";
    let status_label = "✓ Tidak terdeteksi";
    let status_badge: "safe" | "attention" | "high" = "safe";
    let scoreContrib = 0;

    const hardFlagEvidence = ind.code === "R1"
      ? /(?:wajib|harus|diminta)\s*(?:membayar|transfer|bayar|setor|deposit|top\s*up)|(?:transfer|bayar|setor)\s*(?:dulu|biaya|uang|deposit)|deposit\s*(?:awal|sebesar|rp|\d+)|(?:biaya|uang|dana)\s+(?:awal\s+)?(?:pendaftaran|registrasi|administrasi|keberangkatan|pengurusan\s+(?:visa|dokumen))[^.!?\n]{0,100}(?:rp\.?\s*[\d.,]+|\d[\d.,]*\s*(?:rb|ribu|juta))/i.test(cleaned)
      : ind.code === "R6"
      ? /(?:tugas|misi|like|subscribe|follow|rating)[^.!?\n]{0,120}(?:top\s*up|deposit|setor(?:kan)?|transfer|bayar|modal|saldo)|(?:top\s*up|deposit|setor(?:kan)?|transfer|bayar|modal|saldo)[^.!?\n]{0,120}(?:tugas|misi|like|subscribe|follow|rating)/i.test(cleaned)
      : ind.code === "R9"
        ? /(?:tanpa\s*(?:izin\s*)?(?:bp2mi|p3mi)|tidak\s*(?:terdaftar|berizin|terverifikasi).{0,35}(?:bp2mi|p3mi)|visa\s*(?:turis|kunjungan)|tppo|perdagangan\s*orang)/i.test(cleaned)
          || (/(?:kamboja|cambodia|myanmar|laos)/i.test(cleaned)
            && /(?:paspor|passport|visa|pengurusan\s+dokumen|keberangkatan|tiket\s+pesawat)/i.test(cleaned)
            && /(?:biaya\s+(?:awal\s+)?(?:pendaftaran|keberangkatan|visa|dokumen)|rp\.?\s*[\d.,]+[^.!?\n]{0,50}(?:biaya|pendaftaran|visa|dokumen))/i.test(cleaned))
        : true;
    if ((ind.code === "R6" || ind.code === "R9") && !hardFlagEvidence) {
      matches.length = 0;
      evidence = null;
    }
    if (matches.length > 0 && ind.hard_flag && hardFlagEvidence) {
      status = "RISIKO_TINGGI";
      status_label = "! Risiko tinggi";
      status_badge = "high";
      scoreContrib = 0;
      criticalFloor = Math.max(criticalFloor, ind.code === "R9" ? 65 : 80);
      highCount++;
      detectedNames.push(ind.name);
    } else if (matches.length > 0) {
      status = "PERLU_PERHATIAN";
      status_label = "⚠ Perlu diperhatikan";
      status_badge = "attention";
      // A single weak clue contributes less than a repeated, specific pattern.
      // Cap the evidence confidence so keyword-only matches cannot dominate.
      const evidenceConfidence = Math.min(0.78, 0.42 + Math.log2(matches.length + 1) * 0.12);
      const baseRate = RISK_BASE_RATES[ind.code] ?? 0.25;
      const contribution = baseRate * evidenceConfidence;
      combinedRiskProbability = 1 - (1 - combinedRiskProbability) * (1 - contribution);
      scoreContrib = contribution * 100;
      attentionCount++;
      detectedNames.push(ind.name);
    }

    totalScore += scoreContrib;

    return {
      code: ind.code,
      name: ind.name,
      category: ind.category,
      weight,
      status,
      status_label,
      status_badge,
      description: ind.description,
      why_important: ind.why_important,
      matches_count: matches.length,
      evidence
    };
  });

  // Hard evidence contributes its calibrated base rate too; the severity floor
  // ensures a confirmed critical pattern cannot be diluted by unrelated text.
  for (const indicator of detectedIndicators) {
    if (indicator.status === "RISIKO_TINGGI") {
      const baseRate = RISK_BASE_RATES[indicator.code] ?? 0.25;
      combinedRiskProbability = 1 - (1 - combinedRiskProbability) * (1 - baseRate * 0.92);
    }
  }
  totalScore = combinedRiskProbability * 100;
  const finalScore = Math.min(100, Math.max(criticalFloor, Math.round(totalScore)));
  let riskLevel: "RISIKO RENDAH" | "RISIKO SEDANG" | "RISIKO TINGGI" = "RISIKO RENDAH";
  let riskColor: "green" | "amber" | "red" = "green";
  let riskTheme = "#16a34a";
  let levelCode: "LOW" | "MEDIUM" | "HIGH" = "LOW";

  if (finalScore >= 60) {
    riskLevel = "RISIKO TINGGI";
    riskColor = "red";
    riskTheme = "#dc2626";
    levelCode = "HIGH";
  } else if (finalScore >= 25) {
    riskLevel = "RISIKO SEDANG";
    riskColor = "amber";
    riskTheme = "#f59e0b";
    levelCode = "MEDIUM";
  }

  const detectedTopics = detectedIndicators
    .filter((indicator) => indicator.status !== "TIDAK_TERDETEKSI")
    .map((indicator) => indicator.name);
  const findings = detectedTopics.length === 0
    ? "Belum ada tanda risiko utama yang terdeteksi pada teks ini. Skor rendah bukan jaminan lowongan aman; verifikasi perusahaan dan proses rekrutmen secara mandiri."
    : `Tanda yang perlu diperhatikan berkaitan dengan ${detectedTopics.join(", ")}.`;
  const preventiveAdvice = riskLevel === "RISIKO TINGGI"
    ? "Tunda proses lamaran. Jangan transfer uang atau mengirim data sensitif; verifikasi perusahaan melalui kanal resmi yang ditemukan secara mandiri."
    : riskLevel === "RISIKO SEDANG"
      ? "Minta penjelasan tertulis dan verifikasi identitas perekrut serta rincian pekerjaan melalui kanal resmi sebelum melanjutkan."
      : "Tetap periksa identitas perusahaan dan kontak perekrut melalui sumber resmi sebelum membagikan dokumen pribadi.";
  const summary = `${findings} ${preventiveAdvice}`;
  const totalDetected = highCount + attentionCount;

  return {
    id: Date.now(),
    risk_score: finalScore,
    risk_level: riskLevel,
    risk_color: riskColor,
    risk_theme: riskTheme,
    level_code: levelCode,
    summary,
    findings_summary: findings,
    preventive_advice: preventiveAdvice,
    indicators_detected_count: totalDetected,
    indicators_attention_count: attentionCount,
    indicators_high_count: highCount,
    indicators: detectedIndicators,
    verification_steps: VERIFICATION_STEPS,
    disclaimer: "JOBSAFE memberikan penilaian risiko berdasarkan informasi yang tersedia. Hasil ini bukan keputusan hukum atau jaminan bahwa suatu lowongan pasti aman atau penipuan.",
    raw_input: cleaned,
    input_type: "text" as const
  };
}
