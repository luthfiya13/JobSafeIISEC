"""Adapter exposing the hybrid model with the frontend's API contract."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

from app.engine.indicators import DEFAULT_INDICATORS
from app.database.db import get_risk_thresholds

MODEL_PACKAGE_ROOT = Path(__file__).resolve().parents[3] / "Model" / "src" / "jobsafe"
if str(MODEL_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(MODEL_PACKAGE_ROOT))

from jobsafe import JobsafeHybridEngine  # noqa: E402

_MODEL_ENGINE = JobsafeHybridEngine()

LEVEL_MAP = {
    "LOW": ("RISIKO RENDAH", "green", "#16a34a"),
    "MEDIUM": ("RISIKO SEDANG", "amber", "#f59e0b"),
    "HIGH": ("RISIKO TINGGI", "red", "#dc2626"),
}


class RiskAnalyzer:
    def __init__(self):
        # The public/admin legacy indicator table is descriptive only. Scoring
        # always uses the versioned v3 model configuration.
        self.indicators = DEFAULT_INDICATORS
        self.engine = _MODEL_ENGINE

    def indicator_catalog(self) -> List[Dict[str, Any]]:
        model_indicators = self.engine.rule_engine.config.get("indicators", {})
        return [
            {
                "code": configured["code"],
                "name": model_indicators.get(configured["code"], {}).get("name", configured["name"]),
                "category": configured.get("category", "Umum"),
                "description": configured["description"],
                "why_important": configured["why_important"],
            }
            for configured in self.indicators
        ]

    def model_status(self) -> Dict[str, Any]:
        return {
            "engine_version": self.engine.rule_engine.config.get("version", "unknown"),
            "ml_loaded": self.engine.ml_model is not None,
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        cleaned = (text or "").strip()
        if len(cleaned) < 20:
            raise ValueError("Teks lowongan terlalu pendek. Masukkan minimal 20 karakter untuk analisis.")

        low_max, high_min = get_risk_thresholds()
        self.engine.rule_engine.low_max = low_max
        self.engine.rule_engine.high_min = high_min
        model_result = self.engine.analyze(cleaned, mode="hybrid")
        raw_level = model_result.get("risk_level", "MEDIUM")
        if raw_level == "INSUFFICIENT_INPUT":
            message = model_result.get("message", "Informasi lowongan belum cukup untuk dinilai.")
            checklist = model_result.get("verification_checklist", [])
            return {
                "risk_score": None,
                "risk_level": "INSUFFICIENT_INPUT",
                "risk_color": "gray",
                "risk_theme": "#64748b",
                "level_code": "INSUFFICIENT_INPUT",
                "summary": message,
                "findings_summary": message,
                "preventive_advice": "Tempel teks lowongan yang lebih lengkap lalu jalankan analisis kembali.",
                "indicators_detected_count": 0,
                "indicators_attention_count": 0,
                "indicators_high_count": 0,
                "indicators": [],
                "verification_steps": [
                    {"id": f"v{index + 1}", "title": item, "desc": "Lakukan pemeriksaan ini secara mandiri."}
                    for index, item in enumerate(checklist)
                ],
                "disclaimer": model_result.get("disclaimer", ""),
                "model_meta": model_result.get("meta", {}),
                "risk_thresholds": {"low_max": low_max, "high_min": high_min},
            }

        risk_level, risk_color, risk_theme = LEVEL_MAP[raw_level]
        detected_by_code = {item["code"]: item for item in model_result.get("detected_indicators", [])}
        frontend_indicators = []
        high_count = 0
        attention_count = 0

        for configured in self.indicators:
            detected = detected_by_code.get(configured["code"])
            model_indicator = self.engine.rule_engine.config.get("indicators", {}).get(configured["code"], {})
            is_high = bool(detected and (
                detected.get("strength") == "STRONG"
                or (configured.get("hard_flag", False) and configured["code"] in {"R1", "R6", "R9"})
            ))
            if is_high:
                status, status_label, status_badge = "RISIKO_TINGGI", "! Risiko tinggi", "high"
                high_count += 1
            elif detected:
                status, status_label, status_badge = "PERLU_PERHATIAN", "⚠ Perlu diperhatikan", "attention"
                attention_count += 1
            else:
                status, status_label, status_badge = "TIDAK_TERDETEKSI", "✓ Tidak terdeteksi", "safe"

            frontend_indicators.append({
                "code": configured["code"],
                "name": model_indicator.get("name", configured["name"]),
                "category": configured.get("category", "Umum"),
                "status": status,
                "status_label": status_label,
                "status_badge": status_badge,
                "description": configured["description"],
                "why_important": configured["why_important"],
                "matches_count": 1 if detected else 0,
                "evidence": detected.get("evidence") if detected else None,
                "reason": detected.get("reason") if detected else None,
                "legal_basis": detected.get("legal_basis") if detected else None,
                "syariah_basis": detected.get("syariah_basis") if detected else None,
            })

        findings = model_result.get("risk_explanation") or model_result.get("message", "")
        recommendations = model_result.get("recommended_actions", [])
        preventive_advice = " ".join(recommendations)
        checklist = model_result.get("verification_checklist", [])
        return {
            "risk_score": int(model_result.get("risk_score") or 0),
            "risk_level": risk_level,
            "risk_color": risk_color,
            "risk_theme": risk_theme,
            "level_code": raw_level,
            "summary": f"{findings} {preventive_advice}".strip(),
            "findings_summary": findings,
            "preventive_advice": preventive_advice,
            "indicators_detected_count": high_count + attention_count,
            "indicators_attention_count": attention_count,
            "indicators_high_count": high_count,
            "indicators": frontend_indicators,
            "verification_steps": [
                {"id": f"v{index + 1}", "title": item, "desc": "Lakukan pemeriksaan ini secara mandiri."}
                for index, item in enumerate(checklist)
            ],
            "disclaimer": model_result.get("disclaimer", ""),
            "model_meta": model_result.get("meta", {}),
            "risk_thresholds": {"low_max": low_max, "high_min": high_min},
        }
