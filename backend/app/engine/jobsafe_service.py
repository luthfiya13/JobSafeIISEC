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
    from jobsafe.engine import LEVEL_MSG  # noqa: E402
except (ImportError, OSError):
    JobsafeHybridEngine = None  # type: ignore[assignment,misc]
    LEVEL_MSG = {"LOW": "Risiko rendah.", "MEDIUM": "Risiko sedang.", "HIGH": "Risiko tinggi."}
from app.engine.analyzer import RiskAnalyzer
from app.engine.context_llm import ContextLLM

_SERVICE: "JobsafeService | None" = None


class JobsafeService:
    def __init__(self) -> None:
        self.context_llm = ContextLLM()
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
            context_result = self.context_llm.analyze(text)
            if context_result:
                by_code = {item["code"]: item for item in legacy["indicators"]}
                for finding in context_result["findings"]:
                    item = by_code.get(finding["code"])
                    if not item:
                        continue
                    item["evidence"] = finding["evidence"]
                    item["matches_count"] = max(1, item.get("matches_count", 0))
                    if item["status"] == "TIDAK_TERDETEKSI":
                        item.update({
                            "status": "RISIKO_TINGGI" if finding["confidence"] >= 0.7 else "PERLU_PERHATIAN",
                            "status_label": "! Risiko tinggi" if finding["confidence"] >= 0.7 else "⚠ Perlu diperhatikan",
                            "status_badge": "high" if finding["confidence"] >= 0.7 else "attention",
                        })
                risk = sum(
                    float(item.get("weight", 0))
                    for item in legacy["indicators"]
                    if item["status"] in {"RISIKO_TINGGI", "PERLU_PERHATIAN"}
                )
                legacy["risk_score"] = max(legacy["risk_score"], min(100, int(round(risk))))
                if legacy["risk_score"] >= 40:
                    legacy.update({"risk_level": "RISIKO TINGGI", "risk_color": "red", "risk_theme": "#dc2626", "level_code": "HIGH"})
                elif legacy["risk_score"] >= 5:
                    legacy.update({"risk_level": "RISIKO SEDANG", "risk_color": "amber", "risk_theme": "#f59e0b", "level_code": "MEDIUM"})
                legacy["indicators_detected_count"] = sum(item["status"] != "TIDAK_TERDETEKSI" for item in legacy["indicators"])
                legacy["indicators_high_count"] = sum(item["status"] == "RISIKO_TINGGI" for item in legacy["indicators"])
                legacy["indicators_attention_count"] = sum(item["status"] == "PERLU_PERHATIAN" for item in legacy["indicators"])
                legacy["summary"] += " Temuan konteks: " + " ".join(
                    f"{finding['code']} — {finding['reason']} Kutipan: ‘{finding['evidence']}’."
                    for finding in context_result["findings"]
                )
            legacy["model"] = {
                "hybrid_mode": "rule_compatibility_fallback",
                "ml_enabled": False,
                "context_llm_enabled": self.context_llm.enabled,
                "context_llm_used": bool(context_result),
                "context_llm_model": self.context_llm.model if self.context_llm.enabled else None,
                "context_llm_findings": len(context_result["findings"]) if context_result else 0,
            }
            return legacy
        model_result = self.engine.analyze(text, url=url, mode="hybrid")
        if model_result.get("risk_level") == "INSUFFICIENT_INPUT":
            # The public UI has a three-level result contract; retain its existing
            # validation behavior for short but technically analyzable submissions.
            legacy = RiskAnalyzer(indicators=indicators or []).analyze(text)
            legacy["model"] = {"hybrid_mode": "rule_compatibility_for_short_input", "ml_enabled": False}
            return legacy

        # Semantic analysis supplements the trained/rule engines with contextual
        # evidence. Only exact, source-grounded quotations are accepted.
        context_result = self.context_llm.analyze(text)
        context_findings: List[Dict[str, Any]] = []
        if context_result:
            existing = {item["code"]: item for item in model_result.get("detected_indicators", [])}
            for finding in context_result["findings"]:
                previous = existing.get(finding["code"])
                if previous:
                    if finding["confidence"] > float(previous.get("confidence", 0)):
                        previous["confidence"] = finding["confidence"]
                        previous["evidence"] = finding["evidence"]
                        previous["reason"] = finding["reason"]
                        previous["strength"] = "STRONG" if finding["confidence"] >= 0.7 else "MODERATE"
                else:
                    config = self.engine.rule_engine.config["indicators"][finding["code"]]
                    item = {
                        **finding,
                        "name": config["name"],
                        "strength": "STRONG" if finding["confidence"] >= 0.7 else "MODERATE",
                        "legal_basis": config.get("legal", "-"),
                        "syariah_basis": config.get("syariah", "-"),
                    }
                    model_result.setdefault("detected_indicators", []).append(item)
                    existing[finding["code"]] = item
                context_findings.append(finding)

            # Recompute a conservative noisy-OR score from the combined evidence.
            # Existing rule/ML risk can only increase; critical rule floors remain intact.
            combined = 1.0
            for code, item in existing.items():
                weight = float(self.engine.rule_engine.config["indicators"].get(code, {}).get("base_weight", 0))
                confidence = min(1.0, max(0.0, float(item.get("confidence", 0))))
                combined *= 1.0 - weight * confidence
            score = max(int(model_result.get("risk_score") or 0), int(round((1.0 - combined) * 100)))
            if score >= self.engine.rule_engine.high_min:
                level = "HIGH"
            elif score >= self.engine.rule_engine.low_max:
                level = "MEDIUM"
            else:
                level = "LOW"
            model_result["risk_score"] = score
            model_result["risk_level"] = level
            model_result["message"] = LEVEL_MSG[level]
            model_result["risk_explanation"] = " ".join(
                [model_result.get("risk_explanation", "").strip()]
                + [f"Analisis konteks menemukan {item['code']}: {item['reason']} Kutipan: ‘{item['evidence']}’." for item in context_findings]
            ).strip()
            model_result.setdefault("meta", {}).update({
                "context_llm_enabled": True,
                "context_llm_used": True,
                "context_llm_model": self.context_llm.model,
                "context_llm_findings": len(context_findings),
                "context_summary": context_result.get("context_summary", ""),
            })
        else:
            model_result.setdefault("meta", {}).update({
                "context_llm_enabled": self.context_llm.enabled,
                "context_llm_used": False,
                "context_llm_model": self.context_llm.model if self.context_llm.enabled else None,
            })
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
