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
        hard_flag_detected = False
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

            hard_flag_evidence = (
                bool(re.search(r"(?:tugas|misi|like|subscribe|follow|rating)[^.!?\n]{0,120}(?:top\s*up|deposit|setor(?:kan)?|transfer|bayar|modal|saldo)|(?:top\s*up|deposit|setor(?:kan)?|transfer|bayar|modal|saldo)[^.!?\n]{0,120}(?:tugas|misi|like|subscribe|follow|rating)", lower_text))
                if ind["code"] == "R6" else
                bool(re.search(r"(?:tanpa\s*(?:izin\s*)?(?:bp2mi|p3mi)|tidak\s*(?:terdaftar|berizin|terverifikasi).{0,35}(?:bp2mi|p3mi)|visa\s*(?:turis|kunjungan)|tppo|perdagangan\s*orang)", lower_text))
                if ind["code"] == "R9" else True
            )
            if ind["code"] in ("R6", "R9") and not hard_flag_evidence:
                matches = []
                matched_spans = []

            # Determine indicator status and contribution
            weight = ind.get("weight", 10)
            
            if len(matches) > 0 and ind.get("hard_flag", False) and hard_flag_evidence:
                status = "RISIKO_TINGGI"  # ! Risiko tinggi
                status_label = "! Risiko tinggi"
                status_badge = "high"
                score_contrib = 0.0
                hard_flag_detected = True
                high_severity_count += 1
                detected_names.append(ind["name"])
            elif len(matches) > 0:
                status = "PERLU_PERHATIAN"  # ⚠ Perlu diperhatikan
                status_label = "⚠ Perlu diperhatikan"
                status_badge = "attention"
                score_contrib = float(weight)
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
        final_score = 100 if hard_flag_detected else min(100, int(round(total_calculated_score)))

        # Determine Risk Category
        if hard_flag_detected or final_score >= 40:
            risk_level = "RISIKO TINGGI"
            risk_color = "red"
            risk_theme = "#dc2626"
            level_code = "HIGH"
        elif final_score >= 5:
            risk_level = "RISIKO SEDANG"
            risk_color = "amber"
            risk_theme = "#f59e0b"
            level_code = "MEDIUM"
        else:
            risk_level = "RISIKO RENDAH"
            risk_color = "green"
            risk_theme = "#16a34a"
            level_code = "LOW"

        # Explain detected signals and practical prevention steps without reporting counts.
        total_detected = high_severity_count + attention_count
        findings = (
            "Analisis tidak menemukan tanda risiko utama pada informasi yang diberikan."
            if not detected_names else
            f"Tanda yang perlu diperhatikan berkaitan dengan {', '.join(detected_names)}."
        )
        preventive_advice = (
            "Tunda proses lamaran. Jangan transfer uang atau mengirim data sensitif; verifikasi perusahaan melalui kanal resmi yang ditemukan secara mandiri."
            if risk_level == "RISIKO TINGGI" else
            "Minta penjelasan tertulis dan verifikasi identitas perekrut serta rincian pekerjaan melalui kanal resmi sebelum melanjutkan."
            if risk_level == "RISIKO SEDANG" else
            "Tetap periksa identitas perusahaan dan kontak perekrut melalui sumber resmi sebelum membagikan dokumen pribadi."
        )
        summary = f"{findings} {preventive_advice}"

        return {
            "risk_score": final_score,
            "risk_level": risk_level,
            "risk_color": risk_color,
            "risk_theme": risk_theme,
            "level_code": level_code,
            "summary": summary,
            "findings_summary": findings,
            "preventive_advice": preventive_advice,
            "indicators_detected_count": total_detected,
            "indicators_attention_count": attention_count,
            "indicators_high_count": high_severity_count,
            "indicators": detected_indicators,
            "verification_steps": VERIFICATION_STEPS,
            "disclaimer": "JOBSAFE memberikan penilaian risiko berdasarkan informasi yang tersedia. Hasil ini bukan keputusan hukum atau jaminan bahwa suatu lowongan pasti aman atau penipuan."
        }
