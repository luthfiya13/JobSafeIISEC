"""Adapter that exposes the research model through the public API contract."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

MODEL_ROOT = Path(__file__).resolve().parents[3] / "Model"
if str(MODEL_ROOT) not in sys.path:
    sys.path.insert(0, str(MODEL_ROOT))

try:
    # Use the compatibility package so the persisted estimator can resolve
    # its historical ``jobsafe.ml_model`` module path as well.
    from jobsafe.hybrid_engine import JobsafeHybridEngine  # noqa: E402
except (ImportError, OSError):
    JobsafeHybridEngine = None  # type: ignore[assignment,misc]
from app.engine.analyzer import RiskAnalyzer

_SERVICE: "JobsafeService | None" = None


class JobsafeService:
    def __init__(self) -> None:
        self.engine = None
        if JobsafeHybridEngine is not None:
            self.engine = JobsafeHybridEngine(
                config_path=str(MODEL_ROOT / "config/jobsafe_config.json"),
                official_config_path=str(MODEL_ROOT / "config/official_domains.json"),
                ml_model_path=str(MODEL_ROOT / "config/jobsafe_ml_model.pkl"),
            )

    @staticmethod
    def _level_label(level: str) -> tuple[str, str, str]:
        return {
            "LOW": ("RISIKO RENDAH", "green", "#16a34a"),
            "MEDIUM": ("RISIKO SEDANG", "amber", "#f59e0b"),
            "HIGH": ("RISIKO TINGGI", "red", "#dc2626"),
            "INSUFFICIENT_INPUT": ("INPUT BELUM MEMADAI", "amber", "#f59e0b"),
        }.get(level, ("RISIKO SEDANG", "amber", "#f59e0b"))

    def analyze(self, text: str, url: Optional[str] = None, indicators: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        if self.engine is None:
            legacy = RiskAnalyzer(indicators=indicators or []).analyze(text)
            legacy["model"] = {"hybrid_mode": "rule_compatibility_fallback", "ml_enabled": False}
            return legacy
        model_result = self.engine.analyze(text, url=url, mode="hybrid")
        if model_result.get("risk_level") == "INSUFFICIENT_INPUT":
            # The public UI has a three-level result contract; retain its existing
            # validation behavior for short but technically analyzable submissions.
            legacy = RiskAnalyzer(indicators=indicators or []).analyze(text)
            legacy["model"] = {"hybrid_mode": "rule_compatibility_for_short_input", "ml_enabled": False}
            return legacy
        level_code = model_result.get("risk_level", "MEDIUM")
        risk_level, risk_color, risk_theme = self._level_label(level_code)
        score = model_result.get("risk_score")
        score = int(score) if score is not None else 0

        metadata = {item["code"]: item for item in (indicators or [])}
        detected = {item["code"]: item for item in model_result.get("detected_indicators", [])}
        normalized: List[Dict[str, Any]] = []
        for code in sorted(metadata):
            config = metadata[code]
            item = detected.get(code)
            strength = item.get("strength") if item else None
            status = "RISIKO_TINGGI" if strength == "STRONG" else "PERLU_PERHATIAN" if item else "TIDAK_TERDETEKSI"
            badge = "high" if status == "RISIKO_TINGGI" else "attention" if item else "safe"
            normalized.append({
                "code": code,
                "name": config["name"],
                "category": config.get("category", "Umum"),
                "weight": config.get("weight", 0),
                "status": status,
                "status_label": "! Risiko tinggi" if status == "RISIKO_TINGGI" else "⚠ Perlu diperhatikan" if item else "✓ Tidak terdeteksi",
                "status_badge": badge,
                "description": config.get("description", ""),
                "why_important": config.get("why_important", ""),
                "matches_count": 1 if item else 0,
                "evidence": item.get("evidence") if item else None,
            })

        high_count = sum(item["status"] == "RISIKO_TINGGI" for item in normalized)
        attention_count = sum(item["status"] == "PERLU_PERHATIAN" for item in normalized)
        summary = model_result.get("risk_explanation") or model_result.get("message", "")
        return {
            "risk_score": score,
            "risk_level": risk_level,
            "risk_color": risk_color,
            "risk_theme": risk_theme,
            "level_code": level_code if level_code in {"LOW", "MEDIUM", "HIGH"} else "MEDIUM",
            "summary": summary,
            "findings_summary": summary,
            "preventive_advice": "\n".join(model_result.get("recommended_actions", [])),
            "indicators_detected_count": high_count + attention_count,
            "indicators_attention_count": attention_count,
            "indicators_high_count": high_count,
            "indicators": normalized,
            "verification_steps": [
                {"id": f"v{index}", "title": action, "desc": action}
                for index, action in enumerate(model_result.get("verification_checklist", []), 1)
            ],
            "disclaimer": model_result.get("disclaimer", ""),
            "model": model_result.get("meta", {}),
        }


def get_jobsafe_service() -> JobsafeService:
    """Reuse the loaded model; loading a pickle for every request is prohibitively slow."""
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = JobsafeService()
    return _SERVICE
