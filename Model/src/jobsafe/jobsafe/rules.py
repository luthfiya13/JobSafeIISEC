from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from .text_utils import (normalize_text, split_sentences, extract_entities, domain_from_url,
                         SHORTENERS, EMAIL_RE)
from .verification import VerificationLayer

INDICATORS = [f"R{i}" for i in range(1, 11)]
# Repository-level Model directory (this file lives in Model/src/jobsafe/jobsafe).
BASE_DIR = Path(__file__).resolve().parents[3]
OFFICIAL = json.loads((BASE_DIR / "config/official_domains.json").read_text(encoding="utf-8"))
F = re.I | re.S

# Kalimat peringatan/disclaimer ("tidak pernah meminta biaya", "waspada akun palsu") TIDAK boleh
# memicu R1/R3/R4/R6/R10.
DISCLAIMER = re.compile(
    r"(tidak\s+(?:pernah\s+)?(?:memungut|meminta|dipungut|memotong|ada\s+biaya|mengenakan)|bebas\s+biaya|tanpa\s+(?:biaya|pungutan)|"
    r"gratis|tidak\s+berbayar|waspada|hati-?hati|awas|jangan\s+(?:mudah\s+)?percaya|berhati-?hati|"
    r"akun\s+(?:palsu|tidak\s+resmi)|penipuan|hoaks?|hanya\s+(?:melalui|di|via)\s+(?:website|situs|portal|akun)\s+resmi|"
    r"never\s+ask|free\s+of\s+charge|beware)", F)

def evidence(code: str, score: float, span: str, reason: str) -> Dict[str, Any]:
    return {"code": code, "score": round(float(score), 3), "evidence": span.strip()[:300], "reason": reason}

def _first(text: str, patterns: List[str]) -> str:
    for p in patterns:
        m = re.search(p, text, F)
        if m:
            return m.group(0)
    return ""

def _wb(alias: str) -> re.Pattern:
    return re.compile(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])", re.I)

def claimed_orgs_entities(fl: str) -> List[Dict[str, Any]]:
    """Org dianggap 'diklaim sebagai employer' bila disebut di awal teks atau dekat kata rekrutmen/lowongan/PT/bank.
    Penyebutan sepintas (mis. 'packing order Tokopedia') tidak dihitung."""
    out = []
    head = fl[:150]
    for o in OFFICIAL["orgs"]:
        for a in o["aliases"]:
            if _wb(a).search(head) or re.search(r"(?:rekrutmen|lowongan|loker|karir|recruitment|hiring|dibuka|membuka|pt\.?|bank|persero)\s+(?:[a-z.]+\s+){0,2}" + re.escape(a) + r"(?![a-z0-9])", fl):
                out.append(o)
                break
    return out

def _domain_ok(d: str, org: Dict[str, Any]) -> bool:
    ok = set(OFFICIAL["trusted_job_platforms"]) | set(org["domains"]) | set(OFFICIAL["gov_domain_suffixes"])
    return any(d == x or d.endswith("." + x) for x in ok)

def detect(text: str, url: Optional[str] = None) -> Dict[str, Any]:
    full = normalize_text(text)
    # Teks untuk deteksi risiko = tanpa kalimat disclaimer/peringatan resmi
    sents = split_sentences(full)
    body = " ".join(s for s in sents if not DISCLAIMER.search(s))
    t, tl = body, body.lower()
    fl = full.lower()
    ent = extract_entities(full + (" " + url if url else ""))
    res: Dict[str, List[Dict[str, Any]]] = {k: [] for k in INDICATORS}

    orgs = claimed_orgs_entities(fl)
    # Deteksi apakah ada kanal WhatsApp/Telegram dalam teks
    wa_contact = bool(re.search(
        r"\b(?:whatsapp|wa|telegram|dm|inbox|line)\b[^.\n]{0,40}(?:\d|@|link|bio|hubungi)"
        r"|\b(?:link di bio|hubungi wa|via wa|melalui wa|lewat wa|kontak wa|contact wa)\b"
        r"|\b(?:wa|whatsapp)\s*[:\-]?\s*(?:\+?\d{8,}|0\d{8,})"
        r"|\b(?:dikirimkan|informasi)\b.{0,40}\b(?:whatsapp|wa|telegram)\b", fl))
    ctx = {
        "personal_channel": wa_contact,
        "wa_only": wa_contact and not bool(re.search(
            r"\b(?:email|e-?mail|@(?!gmail|yahoo|hotmail|outlook)|situs|website|portal|forms?\.gle|google form|apply|apply at|daftar di|melamar di|karir\.)\b", fl)),
        "startup_umkm": bool(re.search(r"\b(?:startup|umkm|usaha kecil|usaha rumahan|mikro|toko|warung|kedai|bengkel)\b", fl)),
        "generic_email": bool(re.search(r"@(?:gmail|yahoo|hotmail|outlook)\.[a-z.]{2,}", fl)),
        "overseas": bool(re.search(r"\b(?:luar negeri|overseas|kamboja|cambodia|myanmar|laos|filipina|jepang|korea|taiwan|malaysia|singapura|singapore|dubai|timur tengah|australia|thailand|eropa)\b", fl)),
        "url_shortener": any(d in SHORTENERS or d.endswith(".bit.ly") for d in ent["urls"]),
        "disclaimer_present": bool(DISCLAIMER.search(full)),
        "claimed_orgs": [o["name"] for o in orgs],
        "urls": ent["urls"],
    }

    # R1 — biaya/deposit untuk memperoleh pekerjaan
    # Pola utama: ada kata perintah transfer/bayar/setor yang ditujukan ke pelamar
    r1_active = _first(t, [
        r"\b(?:transfer|membayar|bayar|setor|menyetor|wajib\s+(?:membayar|bayar|setor))\b.{0,90}\b(?:biaya|deposit|dp|pendaftaran|registrasi|administrasi|jaminan|seragam|pelatihan|medical|slot|uang\s+(?:pendaftaran|registrasi|administrasi|jaminan|seragam|muka))\b",
        r"\b(?:untuk|agar)\s+(?:mengamankan|mengunci|memastikan)\s+(?:slot|kursi|posisi|kuota)\b.{0,80}\b(?:bayar|transfer|biaya|uang)\b",
        r"\b(?:bawa|siapkan)\s+(?:uang|biaya)\b.{0,80}\b(?:administrasi|pendaftaran|registrasi|seragam)\b",
        r"\b(?:uang muka|advance payment|non.?refundable)\b",
        r"\b(?:biaya|uang|dana)\s+awal\s+(?:pendaftaran|registrasi|keberangkatan|pengurusan)\b",
    ])
    # Pola pasif: hanya menyebut biaya + nominal tanpa kata perintah aktif
    # Ini lebih lemah — bisa jadi sekedar menyebutkan biaya administrasi yang normal
    r1_passive = _first(t, [
        r"\b(?:biaya|uang|dana)\s+(?:pendaftaran|registrasi|administrasi|jaminan|seragam|pelatihan|medical|keberangkatan|visa|dokumen|training)\b.{0,120}\b(?:rp\.?\s?[\d.,]+|rb|ribu|juta|rekening|ditanggung\s+(?:peserta|pelamar)|tidak\s+dapat\s+dikembalikan|dicicil)\b",
    ]) if not r1_active else ""

    # Filter: biaya pendaftaran sangat kecil (< 300rb) tanpa paksaan = sinyal lemah
    def _is_small_fee(span: str) -> bool:
        """True bila nominal dalam span <= 300.000 rupiah (bukan pungutan signifikan)."""
        # Cari semua angka dalam span, periksa apakah ada yang > 300rb
        juta_m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:juta|jt)", span, re.I)
        if juta_m:
            try:
                val = float(juta_m.group(1).replace(",", "."))
                return val <= 0.3  # <= 300 ribu
            except ValueError:
                return False
        ribu_m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:ribu|rb|k)\b", span, re.I)
        if ribu_m:
            try:
                val = float(ribu_m.group(1).replace(",", "."))
                return val <= 300
            except ValueError:
                return False
        # Nominal tanpa satuan: cari "Rp 100.000" / "Rp100000"
        rp_m = re.search(r"rp\.?\s*(\d[\d.,]*)", span, re.I)
        if rp_m:
            try:
                raw = rp_m.group(1).replace(".", "").replace(",", "")
                val = float(raw)
                return val <= 300000
            except ValueError:
                return False
        return False

    r1 = r1_active or r1_passive
    if r1 and re.search(r"\b(?:cod|hasil penjualan|setoran harian|tagihan|pelanggan|kasir|omzet)\b", r1, F):
        r1 = ""  # tugas kerja sah (setor COD/kasir), bukan pungutan atas pelamar
    if r1:
        if r1_active:
            res["R1"].append(evidence("R1", 0.92, r1, "Pembayaran aktif diminta dari pelamar untuk memperoleh/melanjutkan proses rekrutmen."))
        elif r1_passive and not _is_small_fee(r1):
            # Biaya disebutkan pasif + nominal tidak kecil = perlu diperhatikan
            res["R1"].append(evidence("R1", 0.55, r1, "Biaya rekrutmen disebutkan dengan nominal signifikan; konfirmasi apakah pungutan ditanggung perusahaan atau pelamar."))
        # Biaya pasif + nominal kecil (misal 100rb) = TIDAK ditandai sebagai risiko

    # R2 — kompensasi tidak wajar: gaji fantastis ATAU jam kerja sangat singkat + imbalan
    # ——— Ekstrak nominal gaji yang BENAR-BENAR sangat tinggi (>= 20 juta per bulan) ———
    # Gaji 5-7 juta untuk fresh graduate = NORMAL, tidak perlu di-flag
    fantastis = _first(t, [
        # >= 20 juta per bulan (sebelumnya 2 juta sudah trigger — ini salah)
        r"\b(?:gaji|penghasilan|salary|upah)[^.!?\n]{0,30}(?:rp\.?\s*)?(?:[2-9]\d|[1-9]\d{2,})\s*(?:juta|jt)(?:\s*(?:–|-|s/?d)\s*(?:rp\.?\s*)?(?:[2-9]\d|[1-9]\d{2,})\s*(?:juta|jt))?\b",
        # >= 20 juta tanpa konteks kata gaji tapi jelas nominal besar
        r"\b(?:rp\.?\s*)?(?:[2-9]\d|[1-9]\d{2,})\s*(?:juta|jt)(?:\s*(?:/|per)\s*(?:bulan|bln))?\b",
        r"\b(?:\$|usd\s*)\s*(?:[5-9]\d{2}|[1-9]\d{3,})\b",  # USD >= 500
        r"\b(?:rp\.?\s*)?\d{3,}\s*(?:rb|ribu|k)\s*(?:/|per)\s*(?:hari|jam)\b",  # ratusan ribu/hari
        r"\b(?:rp\.?\s*)?[1-9]\d?\s*(?:juta|jt)\s*(?:/|per)\s*(?:hari|minggu)\b",  # juta/hari
    ])
    # Filter: angka yang terdeteksi harus memang >= 20 juta
    def _is_high_salary(span: str) -> bool:
        """True hanya bila nominal gaji dalam span >= 20 juta."""
        juta_m = re.findall(r"(\d+(?:[.,]\d+)?)\s*(?:juta|jt)\b", span, re.I)
        for v in juta_m:
            try:
                if float(v.replace(",", ".")) >= 20:
                    return True
            except ValueError:
                continue
        ribu_m = re.findall(r"(\d+(?:[.,]\d+)?)\s*(?:ribu|rb|k)\s*(?:/|per)\s*(?:hari|jam)", span, re.I)
        for v in ribu_m:
            try:
                if float(v.replace(",", ".")) >= 500:  # >= 500rb/hari = mencurigakan
                    return True
            except ValueError:
                continue
        return False

    high = fantastis if (fantastis and _is_high_salary(fantastis)) else ""

    short_hours = _first(t, [
        r"\b(?:kerja|waktu\s*kerja)\s*(?:hanya|cuma|cukup)?\s*[1-5]\s*jam\b",
        r"\b(?:hanya|cuma|cukup)\s*(?:luangkan\s*waktu\s*)?[1-5]\s*jam\s*(?:sehari|per\s*hari|kerja)?\b",
        r"\b[1-5]\s*jam\s*(?:sehari|per\s*hari)\b.{0,30}\b(?:gaji|penghasilan|dapat|cuan)\b",
    ])
    low_barrier_scam = _first(t, [
        # Hanya trigger bila benar-benar tidak ada kualifikasi APAPUN (bukan sekadar fresh graduate OK)
        r"\b(?:cukup|modal)\s+(?:hp|handphone|android|like|subscribe)\b",
        r"\b(?:santai|mudah|gampang)\b.{0,40}\b(?:gaji|penghasilan|komisi|untung)\b",
        r"\b(?:typing|mengetik|like|subscribe)\b",
        r"\btanpa\s+(?:(?:minimal|batasan)\s+)?(?:skill|keahlian|syarat|bahasa inggris|ijazah)\b",
        r"\btidak\s+(?:wajib|perlu)\s+(?:bisa|pengalaman|ijazah)\b",
    ])

    if high and (short_hours or low_barrier_scam):
        companion = short_hours or low_barrier_scam
        res["R2"].append(evidence("R2", 0.85, f"{high} ... {companion}", "Imbalan sangat tinggi dikombinasikan dengan jam kerja sangat singkat atau tanpa kualifikasi apapun — pola tidak wajar."))
    elif high and re.search(r"\b(?:[5-9]\d|\d{3,})\s*(?:juta|jt)\b", high, re.I):
        res["R2"].append(evidence("R2", 0.78, high, "Tawaran gaji sangat tinggi (di atas 50 juta/bulan) tanpa penjelasan beban kerja yang setara."))
    elif high:
        res["R2"].append(evidence("R2", 0.65, high, "Tawaran penghasilan sangat tinggi (>= 20 juta/bulan) tidak sebanding dengan kualifikasi minimum yang diminta."))
    elif short_hours and re.search(r"\b(?:juta|jt|ribu|rb|dapat|gaji|biaya)\b", t, re.I):
        res["R2"].append(evidence("R2", 0.65, short_hours, "Beban kerja sangat singkat (hanya beberapa jam) dengan klaim imbalan yang mencurigakan."))
    elif low_barrier_scam and re.search(r"\b(?:juta|jt|ribu|rb|gaji|penghasilan)\b", t, re.I):
        res["R2"].append(evidence("R2", 0.55, low_barrier_scam, "Pekerjaan menjanjikan imbalan finansial tanpa kualifikasi/skill apapun."))

    # R3 — data identitas / kredensial
    cred = _first(t, [
        r"\b(?:kirim|berikan|sebutkan|bagikan|input|masukkan|share)\w*\b.{0,40}\b(?:otp|password|kata sandi|pin\b|kode verifikasi|mobile banking|m-?banking)\b",
        r"\b(?:otp|password|kata sandi|kode verifikasi)\b.{0,40}\b(?:kirim|berikan|sebutkan|bagikan)\w*"
    ])
    ident = _first(t, [
        r"\b(?:kirim|upload|unggah|serahkan|lampirkan|kirimkan|foto|fotokopi|input|masukkan|isi|cantumkan|berikan|share)\w*\b.{0,60}\b(?:ktp|e-?ktp|nik|paspor|passport|kk|selfie|foto diri|nomor rekening|no\.? rekening|rekening bank|kartu atm|kartu kredit|data perbankan)\b"
    ])
    if cred:
        res["R3"].append(evidence("R3", 0.97, cred, "Permintaan OTP/password/PIN/kode verifikasi — tidak pernah sah dalam rekrutmen."))
    elif ident:
        chan = bool(re.search(r"\b(?:via|lewat|melalui|ke)\b.{0,20}\b(?:wa|whatsapp|telegram|dm|inbox|chat|link|form|formulir|bio)\b", ident + " " + t[max(0, t.find(ident) - 40): t.find(ident) + len(ident) + 80], F))
        urgent = bool(re.search(r"\b(?:sekarang\s+juga|sebelum\s+(?:interview|seleksi|wawancara)|saat\s+pendaftaran(?:\s+awal)?|pendaftaran\s+awal|untuk\s+(?:daftar|registrasi))\b", tl))
        bank = bool(re.search(r"rekening|atm|kartu kredit", ident, F))
        score = 0.85 if (chan and urgent) else 0.8 if chan else 0.7 if (urgent or bank) else 0.2  # 0.2 = daftar berkas lazim saat melamar
        res["R3"].append(evidence("R3", score, ident, "Permintaan data identitas sensitif" + (" melalui kanal tidak resmi/di tahap awal." if score >= 0.7 else " (daftar berkas lamaran lazim; sinyal lemah).")))

    # R4 — pencatutan employer / tautan tidak sesuai kanal resmi
    r4_expl = _first(t, [r"\b(?:mengatasnamakan|mencatut|mengaku\s+(?:sebagai\s+)?(?:hrd|recruiter|perwakilan))\b.{0,120}"])
    mismatch, shortener_claim, gen_email_claim = "", "", ""
    for o in orgs:
        for d in ent["urls"]:
            if d in SHORTENERS:
                shortener_claim = shortener_claim or f"{o['name']} + {d}"
            elif not _domain_ok(d, o):
                mismatch = mismatch or f"{o['name']} diklaim, tetapi pendaftaran di {d}"
        if ctx["generic_email"] and not any(_domain_ok(d, o) for d in ent["urls"]):
            gen_email_claim = f"{o['name']} diklaim, tetapi kontak memakai email gratisan"
    if mismatch:
        res["R4"].append(evidence("R4", 0.85, mismatch, "Domain pendaftaran tidak sesuai kanal resmi employer yang diklaim."))
    elif gen_email_claim:
        res["R4"].append(evidence("R4", 0.8, gen_email_claim, "Instansi/perusahaan besar jarang memakai email gratisan untuk rekrutmen."))
    elif r4_expl:
        res["R4"].append(evidence("R4", 0.85, r4_expl, "Terdapat indikasi pencatutan identitas employer."))
    elif shortener_claim:
        res["R4"].append(evidence("R4", 0.3, shortener_claim, "Employer terkenal tetapi tautan dipendekkan; perlu cek keaslian (sinyal lemah)."))

    # R5 — informasi minim / omisi material
    # Elemen yang ada dalam lowongan
    has = {
        "role": bool(re.search(r"\b(?:jobdesk|tugas|tanggung jawab|deskripsi pekerjaan|job desc|responsibilit\w+|posisi|dibutuhkan|dicari|membuka\s+lowongan|loker|staff|staf|operator|kurir|sales|teknisi|manager|supervisor|engineer|asisten|helper|driver|waiter|kasir|admin|officer|specialist|intern|internship|rekrutmen|hiring)\b", tl)),
        "duties": bool(re.search(r"\b(?:tugas(?:\s+utama)?\s*(?::|adalah|meliputi|antara lain|terdiri)|tanggung jawab\s*(?::|adalah|meliputi)|bertanggung jawab\s+(?:untuk|dalam|atas)|mengelola|membuat|membuat konten|merancang|mengoperasikan|melayani|menjual|menghitung|menginput|menganalisis|mengawasi|berkoordinasi)\b", tl)),
        "req": bool(re.search(r"\b(?:syarat|kualifikasi|requirements?|qualifications?|pengalaman|fresh\s+graduate|lulusan|min\.?\s*(?:sma|smk|d3|s1|smp)|usia|pria|wanita|pendidikan|keahlian|skill|portfolio)\b", tl)),
        "loc": bool(re.search(r"\b(?:lokasi|penempatan|location|alamat|jl\.|jalan|kantor|cabang|kota|jakarta|bandung|surabaya|semarang|yogyakarta|solo|surakarta|medan|bekasi|tangerang|depok|bogor|karawang|cikarang|bali|remote|wfh|hybrid)\b", tl)),
        "specific_loc": bool(re.search(r"\b(?:jl\.|jalan|gedung|lantai|ruko|komplek|blok|kecamatan|kelurahan|kabupaten|kode pos|rt|rw)\b", tl)),
        "comp": bool(re.search(r"\b(?:gaji|salary|penghasilan|kompensasi|umk|umr|upah|fasilitas|insentif|tunjangan|bpjs|dinas|bonus|uang\s+makan|mess)\b", tl)),
        "company_info": bool(re.search(r"\b(?:pt\.?|cv\.?|perusahaan|company|firma|korporat|tbk|persero|bergerak\s+di|bergerak\s+dalam|bidang\s+usaha)\b", tl)),
    }
    vague = _first(t, [r"\b(?:tanpa\s+syarat|siapa\s+saja\s+bisa|berbagai\s+posisi|banyak\s+posisi|semua\s+posisi)\b"])

    # Deteksi lokasi vague: hanya menyebut wilayah besar / regional tanpa alamat kantor
    loc_vague = has["loc"] and not has["specific_loc"] and not bool(re.search(
        r"\b(?:jl\.|jalan|gedung|lantai|komplek|alamat\s+kantor|kantor\s+(?:pusat|cabang)\s+(?:di|:))\b", tl))

    # Deteksi deskripsi tugas minim: ada nama posisi tapi tidak ada penjelasan TUGAS konkret
    job_no_duties = has["role"] and not has["duties"]

    # Skor R5 berdasarkan kombinasi sinyal
    r5_signals = []
    r5_score = 0.0

    if vague:
        r5_signals.append(vague)
        r5_score = max(r5_score, 0.45)
    if job_no_duties:
        r5_signals.append("Tidak ada deskripsi tugas/tanggung jawab konkret")
        r5_score = max(r5_score, 0.35)
    if loc_vague:
        r5_signals.append("Lokasi hanya menyebut wilayah regional tanpa alamat kantor")
        r5_score = max(r5_score, 0.30)
    if not has["company_info"] and not ent["emails"] and not ent["phones"]:
        r5_signals.append("Tidak ada informasi kontak/profil perusahaan yang dapat diverifikasi")
        r5_score = max(r5_score, 0.30)
    if len(t) < 200 and sum({k: v for k, v in has.items() if k in ("role", "req", "loc", "comp")}.values()) <= 1 and not ent["emails"] and not ent["phones"]:
        r5_signals.append(t[:200])
        r5_score = max(r5_score, 0.30)

    # Kombinasi: tidak ada tugas + lokasi vague = lebih mencurigakan
    if job_no_duties and loc_vague:
        r5_score = min(0.65, r5_score + 0.15)
    # Kombinasi: tidak ada tugas + tidak ada kontak verifikasi
    if job_no_duties and not has["company_info"] and not ent["emails"] and not ent["phones"]:
        r5_score = min(0.65, r5_score + 0.10)

    if r5_signals and r5_score >= 0.25:
        summary = "; ".join(r5_signals[:3])
        res["R5"].append(evidence("R5", round(r5_score, 3), summary, "Lowongan minim informasi material: " + "; ".join([
            s for s in [
                "tidak ada deskripsi tugas konkret" if job_no_duties else "",
                "lokasi tidak spesifik (hanya wilayah regional)" if loc_vague else "",
                "tidak ada kontak/profil perusahaan terverifikasi" if (not has['company_info'] and not ent['emails'] and not ent['phones']) else "",
            ] if s
        ])))

    # R6 — skema tugas/top-up/setoran modal
    r6 = _first(t, [
        r"\b(?:top.?up|deposit(?:\s+modal)?|setor(?:an)?\s+modal|modal\s+awal|saldo\s+awal|aktivasi\s+akun)\b.{0,160}\b(?:tugas|task|komisi|like|subscribe|follow|profit|order)\b",
        r"\b(?:tugas|task|like|subscribe|follow|review|rating)\b.{0,160}\b(?:top.?up|deposit|modal|saldo|setor)\b",
        r"\b(?:terima|menerima)\s+(?:uang|dana)\b.{0,160}\b(?:transfer|kirim)\w*.{0,100}\b(?:rekening pribadi|rekening anda|akun anda)\b",
        r"\b(?:rekrut|ajak)\s+(?:teman|orang|downline)\b.{0,120}\b(?:bayar|deposit|modal|bonus)\b",
        r"\b(?:pasti\s+profit|modal\s+kembali|dana\s+(?:dikembalikan|bisa\s+ditarik))\b",
    ])
    task_only = _first(t, [r"\b(?:like|subscribe|follow)\b.{0,80}\b(?:komisi|bayaran|rp|rb|ribu)\b"])
    if r6:
        res["R6"].append(evidence("R6", 0.94, r6, "Skema tugas/top-up/setoran modal yang tidak lazim untuk hubungan kerja."))
    elif task_only:
        res["R6"].append(evidence("R6", 0.55, task_only, "Pekerjaan 'tugas dibayar per aksi' — pola awal skema tugas berantai."))

    # R7 — travel/akomodasi terikat + biaya/utang (travel disediakan bukan risiko)
    tie = _first(t, [
        r"\b(?:wajib|harus)\b.{0,80}\b(?:agen|travel|akomodasi|mess|asrama|tiket)\b.{0,60}\b(?:kami|tertentu|yang kami tunjuk|penunjukan)\b",
        r"\b(?:wajib|harus)\b.{0,60}\b(?:beli|pesan|booking)\b.{0,40}\b(?:tiket|travel|akomodasi)\b"
    ])
    debt = bool(re.search(r"\b(?:utang|hutang|potong gaji|dipotong|biaya keberangkatan|dana talangan)\b", tl))
    if tie and (debt or res["R1"]):
        res["R7"].append(evidence("R7", 0.7, tie, "Pembelian travel/akomodasi diwajibkan lewat pihak tertentu disertai biaya/utang."))
    elif tie:
        res["R7"].append(evidence("R7", 0.4, tie, "Travel/akomodasi diwajibkan lewat pihak tertentu; perlu verifikasi."))

    # R8 — kanal tidak terverifikasi / rekruter menghambat verifikasi (konteks)
    refuse = _first(t, [
        r"\b(?:recruiter|hrd|admin)\b.{0,100}\b(?:menolak|melarang|tidak\s+bisa)\b.{0,90}\b(?:verifikasi|menghubungi perusahaan|kanal resmi)\b",
        r"\b(?:jangan|tidak\s+perlu)\b.{0,60}\b(?:cek|verifikasi|tanya)\b"
    ])
    # Deteksi: komunikasi rekrutmen HANYA via WhatsApp/Telegram tanpa alamat kantor/email resmi
    wa_evidence = _first(t, [
        r"\b(?:kandidat\s+terpilih|informasi\s+(?:lanjutan|lebih\s+lanjut)|pengumuman|hasil\s+seleksi|dihubungi)\b.{0,80}\b(?:whatsapp|wa|telegram|dm|chat)\b",
        r"\b(?:hubungi|contact|kontak)\b.{0,40}\b(?:whatsapp|wa|telegram)\b",
        r"\b(?:whatsapp|wa)\b.{0,40}\b(?:\+?\d{8,}|0\d{8,})\b",
        r"\b(?:dikirimkan|diinformasikan)\b.{0,60}\b(?:melalui|via|lewat)\b.{0,30}\b(?:whatsapp|wa|telegram)\b",
    ])
    has_official_contact = bool(
        ent["emails"] and not all(re.search(r"@(?:gmail|yahoo|hotmail|outlook)\.", e, re.I) for e in ent["emails"])
    ) or bool(re.search(
        r"\b(?:website|situs|portal|careers?\.?|jobs?\.?|karir\.?|rekrutmen\.?)\s*(?:[:\-]|di|at)?\s*(?:https?://|www\.)"
        r"|\b(?:apply|daftar|melamar)\s+(?:di|via|at|melalui)\s+(?:https?://|www\.)"
        r"|\b(?:email|e-?mail)\s*(?::|ke)?\s*\S+@\S+\.(?:co\.id|com|id|org)"
        , tl))
    if refuse:
        res["R8"].append(evidence("R8", 0.8, refuse, "Rekruter menghambat verifikasi independen."))
    elif ent["foreign_phones"]:
        res["R8"].append(evidence("R8", 0.5, ent["foreign_phones"][0], "Kontak berkode negara asing pada lowongan berbahasa Indonesia."))
    elif orgs and ctx["personal_channel"] and not ent["urls"]:
        res["R8"].append(evidence("R8", 0.4, ", ".join(o["name"] for o in orgs), "Employer besar diklaim tetapi pendaftaran hanya via kontak/DM personal."))
    elif wa_evidence and ctx.get("wa_only") and not has_official_contact and not has.get("specific_loc", False):
        # WhatsApp-only rekrutmen + tanpa alamat kantor + tanpa email/situs resmi
        res["R8"].append(evidence("R8", 0.45, wa_evidence,
            "Proses rekrutmen hanya melalui WhatsApp/Telegram tanpa kontak resmi perusahaan (email domain, website, atau alamat kantor) yang dapat diverifikasi."))

    # R9 — TPPO / migrasi non-prosedural / scam hubs (butuh konteks luar negeri)
    sig_pat = {
        "tanpa_izin": r"\b(?:tanpa izin|ilegal|non.?prosedural|jalur khusus|tidak perlu visa kerja|visa (?:turis|wisata|kunjungan))\b",
        "cepat": r"\b(?:fly in|berangkat (?:cepat|langsung|minggu depan)|\d+\s*hari\s+(?:berangkat|terbang)|terbang\s+\d+\s*hari)\b",
        "bahasa": r"\b(?:tidak\s+(?:wajib|perlu)\s+bisa\s+bahasa|tanpa\s+bahasa)\b",
        "utang": r"\b(?:dana talangan|utang|hutang|potong gaji|biaya (?:berangkat|keberangkatan) ditanggung)\b",
        "tahan": r"\b(?:paspor ditahan|dokumen ditahan|dilarang keluar|kerja paksa)\b",
        "p3mi_hilang": r"\b(?:tanpa p3mi|tanpa bp2mi|agen tidak jelas|penempatan tidak jelas)\b"
    }
    sigs = [k for k, p in sig_pat.items() if re.search(p, tl)]
    scam_dest = bool(re.search(r"\b(?:kamboja|cambodia|myanmar|laos|filipina)\b", tl)) and bool(re.search(r"\b(?:customer service|cs|admin|operator|telemarketing|typing|online)\b", tl))
    high_risk_destination = _first(t, [r"\b(?:kamboja|cambodia|myanmar|laos)\b"])
    migration_paperwork = _first(t, [
        r"\b(?:paspor|passport|visa|pengurusan dokumen|dokumen dan visa|keberangkatan|tiket pesawat|penempatan)\b[^.!?\n]{0,90}",
        r"\b(?:paspor|passport|visa|pengurusan dokumen|dokumen dan visa|keberangkatan|tiket pesawat|penempatan)\b"
    ])
    migration_fee = _first(t, [
        r"\b(?:biaya|uang|dana)\s+(?:awal\s+)?(?:pendaftaran|keberangkatan|visa|dokumen|pengurusan)\b[^.!?\n]{0,100}",
        r"\b(?:rp\.?\s?[\d.,]+)\b[^.!?\n]{0,50}\b(?:biaya|pendaftaran|visa|dokumen|keberangkatan)\b"
    ])
    # Destination alone is not treated as evidence of trafficking. The
    # combination of a high-risk destination, employer-arranged migration
    # paperwork, and an upfront recruitment/departure fee is a strong cluster.
    migration_fee_cluster = bool(high_risk_destination and migration_paperwork and migration_fee)
    if ctx["overseas"] or scam_dest:
        if "tahan" in sigs or len(sigs) >= 2 or (scam_dest and sigs):
            res["R9"].append(evidence("R9", 0.9, _first(t, list(sig_pat.values())) or "Kamboja/Myanmar/Laos + pekerjaan online", "Kombinasi sinyal migrasi non-prosedural/eksploitasi."))
        elif migration_fee_cluster:
            res["R9"].append(evidence(
                "R9", 0.86,
                f"{high_risk_destination} ... {migration_paperwork.strip()} ... {migration_fee.strip()}",
                "Tujuan kerja luar negeri digabung dengan pengurusan paspor/visa dan pungutan awal dari pelamar; verifikasi izin penempatan dan biaya secara independen."
            ))
        elif scam_dest:
            res["R9"].append(evidence("R9", 0.8, "Lokasi berisiko tinggi + pekerjaan online/CS", "Pola rekrutmen ke pusat penipuan online (Kamboja/Myanmar/Laos)."))
        elif len(sigs) == 1:
            res["R9"].append(evidence("R9", 0.55, _first(t, list(sig_pat.values())), "Satu sinyal migrasi berisiko pada lowongan luar negeri."))

    # R10 — tekanan waktu + tindakan berisiko
    urg = bool(re.search(r"\b(?:kuota\s+terbatas|slot\s+(?:terakhir|terbatas)|tempat\s+terbatas|sekarang\s+juga|hari\s+ini\s+(?:juga|terakhir)|panggilan\s+instan|buruan|jangan\s+sampai\s+(?:ketinggalan|kehabisan))\b", tl))
    act = _first(t, [r"\b(?:transfer|bayar|setor|deposit|kirim\s+(?:ktp|data|foto)|scan\s+(?:qr|barcode)|klik\s+link)\b"])
    noverify = _first(t, [r"\b(?:jangan|tidak\s+perlu)\b.{0,80}\b(?:tanya|verifikasi|hubungi|cek)\b.{0,100}\b(?:hr|perusahaan|kantor|resmi)\b"])
    if noverify:
        res["R10"].append(evidence("R10", 0.75, noverify, "Penekanan agar tidak memverifikasi."))
    elif urg and act:
        res["R10"].append(evidence("R10", 0.7, act, "Tekanan waktu dikaitkan dengan tindakan berisiko."))
    elif urg:
        res["R10"].append(evidence("R10", 0.3, "tekanan waktu", "Tekanan waktu/kelangkaan (sinyal lemah; batas waktu biasa tidak dihitung)."))

    return {"indicators": res, "context": ctx, "entities": ent, "claimed_org_objects": orgs}


def best_scores(detected: Dict[str, Any]) -> Dict[str, float]:
    return {k: (max(x["score"] for x in v) if v else 0.0) for k, v in detected["indicators"].items()}
