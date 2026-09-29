import re
from typing import List, Dict, Any, Optional
from app.engine.indicators import DEFAULT_INDICATORS, VERIFICATION_STEPS

class RiskAnalyzer:
    def __init__(self, indicators: Optional[List[Dict[str, Any]]] = None):
        self.indicators = indicators if indicators is not None else DEFAULT_INDICATORS

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        # Preserve newlines but normalize multiple spaces
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    def find_snippet(self, text: str, matched_span: tuple, window: int = 70) -> str:
        start, end = matched_span
        snippet_start = max(0, start - window)
        snippet_end = min(len(text), end + window)
        
        snippet = text[snippet_start:snippet_end].strip()
        # Clean line breaks in snippet for neat display
        snippet = " ".join(snippet.split())
        
        prefix = "..." if snippet_start > 0 else ""
        suffix = "..." if snippet_end < len(text) else ""
        return f'{prefix}"{snippet}"{suffix}'

    def analyze(self, text: str) -> Dict[str, Any]:
        cleaned = self.clean_text(text)
        lower_text = cleaned.lower()

        if len(cleaned) < 15:
            raise ValueError("Teks lowongan terlalu pendek. Masukkan minimal 15 karakter untuk analisis.")

        detected_indicators = []
        total_calculated_score = 0.0
        high_severity_count = 0
        attention_count = 0
        detected_names = []

        for ind in self.indicators:
            if not ind.get("is_active", True):
                continue

            matches = []
            matched_spans = []

            # 1. Regex patterns check
            for pattern in ind.get("patterns", []):
                for match in re.finditer(pattern, lower_text, re.IGNORECASE):
                    matched_spans.append(match.span())
                    matches.append(match.group(0))

            # 2. Keyword check (if not already found by regex)
            if not matches:
                for kw in ind.get("keywords", []):
                    idx = lower_text.find(kw.lower())
                    if idx != -1:
                        matched_spans.append((idx, idx + len(kw)))
                        matches.append(kw)

            # Determine indicator status and contribution
            weight = ind.get("weight", 10)
            
            if len(matches) >= 2 or (len(matches) >= 1 and weight >= 15):
                status = "RISIKO_TINGGI"  # ! Risiko tinggi
                status_label = "! Risiko tinggi"
                status_badge = "high"
                score_contrib = weight * 1.0
                high_severity_count += 1
                detected_names.append(ind["name"])
            elif len(matches) == 1:
                status = "PERLU_PERHATIAN"  # ⚠ Perlu diperhatikan
                status_label = "⚠ Perlu diperhatikan"
                status_badge = "attention"
                score_contrib = weight * 0.75
                attention_count += 1
                detected_names.append(ind["name"])
            else:
                status = "TIDAK_TERDETEKSI"  # ✓ Tidak terdeteksi
                status_label = "✓ Tidak terdeteksi"
                status_badge = "safe"
                score_contrib = 0.0

            evidence = None
            if matched_spans:
                # Get the best snippet
                evidence = self.find_snippet(cleaned, matched_spans[0])

            total_calculated_score += score_contrib

            detected_indicators.append({
                "code": ind["code"],
                "name": ind["name"],
                "category": ind.get("category", "Umum"),
                "weight": weight,
                "status": status,
                "status_label": status_label,
                "status_badge": status_badge,
                "description": ind["description"],
                "why_important": ind["why_important"],
                "matches_count": len(matches),
                "evidence": evidence
            })

        # Cap score at 100 and round
        final_score = min(100, int(round(total_calculated_score)))

        # Determine Risk Category
        if final_score >= 70:
            risk_level = "RISIKO TINGGI"
            risk_color = "red"
            risk_theme = "#dc2626"
            level_code = "HIGH"
        elif final_score >= 30:
            risk_level = "RISIKO SEDANG"
            risk_color = "amber"
            risk_theme = "#f59e0b"
            level_code = "MEDIUM"
        else:
            risk_level = "RISIKO RENDAH"
            risk_color = "green"
            risk_theme = "#16a34a"
            level_code = "LOW"

        # Generate Ringkasan (Executive Summary)
        total_detected = high_severity_count + attention_count
        if total_detected == 0:
            summary = (
                "Tidak ditemukan indikator risiko mencurigakan dari teks lowongan yang Anda periksa. "
                "Secara umum format dan kriteria terlihat wajar. Namun, tetap lakukan verifikasi mandiri sebelum memberikan data pribadi."
            )
        elif risk_level == "RISIKO TINGGI":
            prominent = ", ".join(detected_names[:3])
            summary = (
                f"Lowongan ini memiliki indikator kuat yang perlu diwaspadai, terutama terkait {prominent}. "
                "Pola ini sering dijumpai pada modus penipuan berkedok rekrutmen. Sangat disarankan untuk tidak mentransfer uang atau mengirim dokumen berharga."
            )
        elif risk_level == "RISIKO SEDANG":
            prominent = ", ".join(detected_names[:2])
            summary = (
                f"Lowongan ini memiliki beberapa indikator yang perlu diperhatikan, terutama {prominent}. "
                "Terdapat ketidakjelasan atau kejanggalan dalam deskripsi, lakukan konfirmasi ke sumber resmi sebelum melamar."
            )
        else:
            summary = (
                "Sebagian besar indikator risiko tidak terdeteksi. Risiko relatif rendah, namun pastikan tetap memeriksa keabsahan kontak dan reputasi perusahaan."
            )

        return {
            "risk_score": final_score,
            "risk_level": risk_level,
            "risk_color": risk_color,
            "risk_theme": risk_theme,
            "level_code": level_code,
            "summary": summary,
            "indicators_detected_count": total_detected,
            "indicators_attention_count": attention_count,
            "indicators_high_count": high_severity_count,
            "indicators": detected_indicators,
            "verification_steps": VERIFICATION_STEPS,
            "disclaimer": "JOBSAFE memberikan penilaian risiko berdasarkan informasi yang tersedia. Hasil ini bukan keputusan hukum atau jaminan bahwa suatu lowongan pasti aman atau penipuan."
        }
