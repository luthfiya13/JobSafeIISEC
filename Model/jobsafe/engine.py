from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from .rules import detect, best_scores
from .text_utils import extract_entities, normalize_text
from .verification import VerificationLayer

DISCLAIMER_ID = (
    "Hasil ini adalah penilaian indikasi risiko rekrutmen berbasis analisis teks yang Anda berikan, "
    "bukan vonis hukum dan bukan jaminan keamanan mutlak. Selalu lakukan verifikasi mandiri (tabayyun) "
    "melalui kanal resmi perusahaan terkait."
)

LEVEL_MSG = {
    "HIGH": "Risiko Tinggi: ditemukan indikator kuat/kombinasi indikator yang lazim pada penipuan rekrutmen atau eksploitasi kerja. Sangat disarankan tidak melanjutkan sebelum verifikasi independen.",
    "MEDIUM": "Risiko Sedang: terdapat indikator yang memerlukan kehati-hatian dan klarifikasi. Jangan mentransfer dana atau mengirim data sensitif sebelum keabsahan rekruter terkonfirmasi.",
    "LOW": "Risiko Rendah: tidak terdeteksi indikator risiko signifikan pada teks lowongan yang diberikan. Tetap lakukan verifikasi mandiri sebelum melamar.",
    "INSUFFICIENT_INPUT": "Teks masukan terlalu pendek atau tidak memuat informasi lowongan yang memadai. Silakan tempel teks lengkap atau unggah poster lowongan kerja.",
}

REC = {
    "R1": "Jangan pernah mentransfer biaya pendaftaran, uang seragam, uang pelatihan, atau deposit apa pun dalam proses seleksi kerja.",
    "R2": "Waspadai penawaran gaji tinggi yang tidak sebanding dengan kualifikasi atau beban kerja ringan; mintalah rincian kontrak kerja resmi.",
    "R3": "Jangan mengirimkan data sensitif (foto KTP, KK, buku tabungan) via chat pribadi pada tahap awal pendaftaran; jangan pernah membagikan OTP/PIN/password.",
    "R4": "Ketik sendiri alamat situs resmi perusahaan di peramban dan cocokkan apakah lowongan terdaftar di portal karir resmi.",
    "R5": "Mintalah kejelasan deskripsi pekerjaan, lokasi penempatan, dan profil perusahaan sebelum membagikan dokumen lamaran.",
    "R6": "Pekerjaan berbasis tugas berbayar (like/subscribe/order) yang mewajibkan setoran/top-up modal adalah pola manipulatif; segera hentikan interaksi.",
    "R7": "Jangan menyetujui pembebanan biaya travel/akomodasi sepihak melalui agen tertentu yang mengikat pelamar dengan utang talangan.",
    "R8": "Konfirmasi identitas rekruter melalui nomor kontak kantor atau email domain resmi perusahaan, bukan kontak personal yang tertera di poster.",
    "R9": "Untuk peluang kerja luar negeri, pastikan penempatan melalui P3MI berizin resmi BP2MI/KP2MI dan menggunakan visa kerja resmi, bukan visa turis.",
    "R10": "Abaikan intimidasi atau desakan batas waktu singkat; proses rekrutmen profesional selalu memberikan waktu wajar bagi kandidat.",
}

class JobsafeEngine:
    """
    JOBSAFE Explainable Risk Assessment Engine (v3.0.0).
    Rule-first, context-aware, ordinal recruitment risk evaluation.
    """
    def __init__(self, config_path: Optional[str] = None, official_config_path: Optional[str] = None):
        p = Path(config_path) if config_path else Path(__file__).resolve().parents[1] / "config/jobsafe_config.json"
        self.config = json.loads(p.read_text(encoding="utf-8"))
        self.low_max = self.config["thresholds_bootstrap"]["low_max"]
        self.high_min = self.config["thresholds_bootstrap"]["high_min"]
        self.verifier = VerificationLayer(official_config_path)

    def _noisy_or(self, scores: Dict[str, float]) -> float:
        p = 1.0
        for code, s in scores.items():
            if s > 0:
                p *= 1 - self.config["indicators"][code]["base_weight"] * s
        return (1 - p) * 100

    def _dimensions(self, scores: Dict[str, float]) -> Dict[str, float]:
        out = {}
        for d, codes in self.config["dimensions"].items():
            p = 1.0
            for c in codes:
                if scores.get(c, 0) > 0:
                    p *= 1 - self.config["indicators"][c]["base_weight"] * scores[c]
            out[d] = round((1 - p) * 100, 1)
        return out

    def _floors(self, score: float, scores: Dict[str, float]):
        applied = []
        for r in self.config["floor_rules"]:
            ok = all(scores.get(c, 0) >= th for c, th in r["if_all"])
            if ok and r.get("any"):
                ok = any(scores.get(c, 0) >= th for c, th in r["any"])
            if ok:
                score = max(score, float(r["min_score"]))
                applied.append(r["name"])
        return min(100.0, score), applied

    @staticmethod
    def _quality(text: str) -> str:
        n = len(text)
        return "LOW" if n < 60 else ("MEDIUM" if n < 180 else "OK")

    def _build_risk_explanation(self, level: str, inds: List[Dict[str, Any]], verif: Dict[str, Any]) -> str:
        if level == "INSUFFICIENT_INPUT":
            return LEVEL_MSG["INSUFFICIENT_INPUT"]
        if not inds:
            if verif.get("status") == "VERIFIED":
                return "Teks lowongan tidak memuat indikator risiko rekrutmen dan terhubung dengan kanal resmi yang terverifikasi."
            return "Tidak ditemukan indikator risiko penipuan yang mencurigakan pada teks lowongan ini. Tetap periksa keabsahan rekruter sebelum mengirim data pribadi."
        
        strong_inds = [i for i in inds if i["strength"] == "STRONG"]
        mod_inds = [i for i in inds if i["strength"] == "MODERATE"]
        
        parts = []
        if strong_inds:
            names = [f"{i['name']} ({i['code']})" for i in strong_inds]
            parts.append(f"Terdeteksi indikator risiko mayor: {', '.join(names)}.")
        if mod_inds:
            names = [f"{i['name']} ({i['code']})" for i in mod_inds]
            parts.append(f"Ditemukan sinyal peringatan: {', '.join(names)}.")
        
        if verif.get("status") == "CONTRADICTORY":
            parts.append(f"Catatan verifikasi identitas: {verif['details']}")
            
        return " ".join(parts)

    def analyze(self, text: str, url: Optional[str] = None) -> Dict[str, Any]:
        text = normalize_text(text)[:20000]
        if len(text) < 20:
            return {
                "risk_score": None,
                "risk_level": "INSUFFICIENT_INPUT",
                "detected_indicators": [],
                "evidence": [],
                "dimension_scores": {},
                "verification_status": {
                    "status": "UNVERIFIED",
                    "claimed_employer": None,
                    "official_domain_match": False,
                    "application_channel": "none",
                    "details": "Input terlalu pendek untuk diverifikasi."
                },
                "context_flags": {"url_only": bool(url)},
                "risk_explanation": LEVEL_MSG["INSUFFICIENT_INPUT"],
                "recommended_actions": ["Tempel teks lowongan lengkap atau unggah poster lowongan kerja."],
                "disclaimer": DISCLAIMER_ID,
                # Backward compatibility fields
                "message": LEVEL_MSG["INSUFFICIENT_INPUT"],
                "dimensions": {},
                "indicators": [],
                "recommendations": ["Tempel teks lowongan lengkap atau unggah poster lowongan kerja."],
                "verification_checklist": [
                    "Ketik sendiri alamat situs resmi perusahaan dan cari halaman karir di sana.",
                    "Hubungi perusahaan lewat kontak resmi untuk konfirmasi lowongan.",
                    "Pastikan tidak ada biaya apa pun dalam proses seleksi."
                ],
                "context": {"url_only": bool(url)},
                "meta": {
                    "engine_version": self.config["version"],
                    "input_quality": "LOW",
                    "base_score": None,
                    "floors_applied": [],
                    "rule_only": True,
                    "ml_enabled": False
                }
            }

        d = detect(text, url)
        scores = best_scores(d)
        base = self._noisy_or(scores)
        score, floors = self._floors(base, scores)
        level = "LOW" if score < self.low_max else ("MEDIUM" if score < self.high_min else "HIGH")
        
        # Teks sangat pendek tanpa indikator tidak boleh langsung disebut LOW definitif
        if self._quality(text) == "LOW" and level == "LOW":
            level, score = "MEDIUM", max(score, float(self.low_max))

        inds = []
        evidence_list = []
        for c in [f"R{i}" for i in range(1, 11)]:
            if scores[c] > 0:
                item = max(d["indicators"][c], key=lambda x: x["score"])
                cfg = self.config["indicators"][c]
                strength = "STRONG" if scores[c] >= 0.7 else ("MODERATE" if scores[c] >= 0.45 else "WEAK")
                ind_obj = {
                    "code": c,
                    "name": cfg["name"],
                    "confidence": scores[c],
                    "strength": strength,
                    "evidence": item["evidence"],
                    "reason": item["reason"],
                    "legal_basis": cfg["legal"],
                    "syariah_basis": cfg["syariah"]
                }
                inds.append(ind_obj)
                evidence_list.append(f"[{c}] {item['evidence']} ({item['reason']})")

        rec = [REC[i["code"]] for i in inds if i["strength"] != "WEAK" or i["code"] in ("R1", "R6")]
        if not rec:
            rec = ["Verifikasi identitas pemberi kerja lewat situs/portal resmi dan jangan pernah membayar biaya apa pun untuk melamar."]

        # Verification layer analysis
        verif_res = self.verifier.verify(
            claimed_orgs=d.get("claimed_org_objects", []),
            entities=d["entities"],
            context=d["context"]
        )

        dim_scores = self._dimensions(scores)
        ctx = d["context"]
        context_flags = {
            "personal_channel": ctx["personal_channel"],
            "generic_email": ctx["generic_email"],
            "url_shortener": ctx["url_shortener"],
            "startup_umkm": ctx["startup_umkm"],
            "overseas": ctx["overseas"],
            "disclaimer_present": ctx["disclaimer_present"],
            "claimed_orgs": ctx["claimed_orgs"],
            "urls": ctx["urls"],
            "phones": d["entities"]["phones"],
            "foreign_phones": d["entities"]["foreign_phones"],
            "emails": d["entities"]["emails"]
        }

        risk_explanation = self._build_risk_explanation(level, inds, verif_res)

        checklist = [
            "Ketik sendiri alamat situs resmi perusahaan dan cari informasi lowongan di portal karir resminya.",
            "Hubungi saluran komunikasi resmi perusahaan (bukan nomor kontak personal di poster) untuk konfirmasi keabsahan.",
            "Pastikan tidak ada biaya apa pun (pendaftaran, seragam, pelatihan, deposit) selama tahap seleksi.",
            "Jangan pernah memberikan kode OTP, PIN, password, atau foto dokumen identitas tanpa kejelasan kontrak.",
            "Untuk lowongan kerja luar negeri: pastikan memiliki izin penempatan P3MI/BP2MI dan kontrak kerja tertulis."
        ]

        return {
            "risk_score": int(round(score)),
            "risk_level": level,
            "detected_indicators": inds,
            "evidence": evidence_list,
            "dimension_scores": dim_scores,
            "verification_status": verif_res,
            "context_flags": context_flags,
            "risk_explanation": risk_explanation,
            "recommended_actions": rec,
            "disclaimer": DISCLAIMER_ID,
            # Backward compatibility fields for frontend / existing clients
            "message": LEVEL_MSG[level],
            "dimensions": dim_scores,
            "indicators": inds,
            "recommendations": rec,
            "verification_checklist": checklist,
            "context": {k: ctx[k] for k in ("personal_channel", "generic_email", "url_shortener", "startup_umkm", "overseas", "claimed_orgs", "urls")},
            "meta": {
                "engine_version": self.config["version"],
                "input_quality": self._quality(text),
                "base_score": round(base, 1),
                "floors_applied": floors,
                "rule_only": True,
                "ml_enabled": False
            }
        }
