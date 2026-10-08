from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from .engine import JobsafeEngine, DISCLAIMER_ID, LEVEL_MSG
from .ml_model import JobsafeMLModel, CLASSES
from .text_utils import normalize_text

BASE_DIR = Path(__file__).resolve().parents[3]

class JobsafeHybridEngine:
    """
    JOBSAFE Hybrid Explainable Risk Assessment Engine.
    Combines rule-first expert knowledge (hard floors, verification layer, indicator evidence)
    with statistical machine learning (TF-IDF + Calibrated Linear Classifier).
    
    Philosophy:
    - Conservative Gating: Rule floor overrides ML if a critical scam pattern (R1, R3 credentials, R6, R9) is detected.
    - Soft Blending: For ambiguous/moderate cases, blends rule confidence with ML calibrated probability.
    - Graceful Fallback: Seamlessly falls back to rule-first mode if ML weights are unavailable.
    """
    def __init__(
        self,
        config_path: Optional[str] = None,
        official_config_path: Optional[str] = None,
        ml_model_path: Optional[Union[str, Path]] = None
    ):
        self.rule_engine = JobsafeEngine(config_path, official_config_path)
        self.ml_model: Optional[JobsafeMLModel] = None
        
        # Attempt to load ML model if specified or if default model exists
        target_ml_path = ml_model_path or BASE_DIR / "config/jobsafe_ml_model.pkl"
        p = Path(target_ml_path)
        if p.exists():
            try:
                self.ml_model = JobsafeMLModel.load(p)
            except Exception as ex:
                print(f"[WARN] Could not load ML model from {p}: {ex}. Running in rule-first fallback mode.")

    def analyze(
        self,
        text: str,
        url: Optional[str] = None,
        mode: str = "hybrid" # 'hybrid' | 'rule_only' | 'ml_only'
    ) -> Dict[str, Any]:
        # If rule-only mode or ML not loaded, delegate directly to rule engine
        if mode == "rule_only" or self.ml_model is None:
            res = self.rule_engine.analyze(text, url)
            res["meta"]["hybrid_mode"] = "rule_only"
            return res

        # Run Rule Engine Analysis
        rule_res = self.rule_engine.analyze(text, url)
        
        # If input is insufficient, return immediately
        if rule_res["risk_level"] == "INSUFFICIENT_INPUT":
            return rule_res

        # Run ML Analysis
        clean_text = normalize_text(text)
        ml_res = self.ml_model.predict_single(clean_text)
        
        if mode == "ml_only":
            ml_level = ml_res["ml_predicted_level"]
            ml_score = ml_res["ml_risk_score"]
            res = rule_res.copy()
            res["risk_score"] = ml_score
            res["risk_level"] = ml_level
            res["message"] = LEVEL_MSG[ml_level]
            res["meta"]["hybrid_mode"] = "ml_only"
            res["meta"]["ml_enabled"] = True
            res["meta"]["ml_details"] = ml_res
            return res

        # HYBRID BLENDING LOGIC
        rule_score = rule_res["risk_score"] or 0
        rule_level = rule_res["risk_level"]
        ml_score = ml_res["ml_risk_score"]
        ml_level = ml_res["ml_predicted_level"]
        floors_applied = rule_res["meta"].get("floors_applied", [])
        
        # Check if critical floor rule was applied
        is_critical_floor = bool(floors_applied) or any(
            i["code"] in ("R1", "R6", "R9") and i["strength"] == "STRONG"
            for i in rule_res["detected_indicators"]
        )

        if is_critical_floor or rule_score >= 70:
            # Conservative rule override: severe scam cannot be downgraded by ML
            final_score = max(rule_score, int(round(0.7 * rule_score + 0.3 * ml_score)))
            override_reason = "CRITICAL_RULE_FLOOR_OVERRIDE"
        elif rule_level == "LOW" and ml_level == "HIGH" and ml_res["class_probabilities"]["HIGH"] > 0.75:
            # Statistical anomaly flag: ML detects strong scam signals missed by exact regex
            final_score = max(int(self.rule_engine.low_max), int(round(0.4 * rule_score + 0.6 * ml_score)))
            override_reason = "ML_STATISTICAL_ESCALATION"
        else:
            # Balanced ensemble blend (60% Rule, 40% ML)
            final_score = int(round(0.6 * rule_score + 0.4 * ml_score))
            override_reason = "BALANCED_ENSEMBLE"

        # Final ordinal classification
        if final_score < self.rule_engine.low_max:
            final_level = "LOW"
        elif final_score < self.rule_engine.high_min:
            final_level = "MEDIUM"
        else:
            final_level = "HIGH"

        # Construct final output
        res = rule_res.copy()
        res["risk_score"] = final_score
        res["risk_level"] = final_level
        res["message"] = LEVEL_MSG[final_level]
        res["meta"]["hybrid_mode"] = "hybrid"
        res["meta"]["ml_enabled"] = True
        res["meta"]["rule_score"] = rule_score
        res["meta"]["ml_score"] = ml_score
        res["meta"]["ml_details"] = ml_res
        res["meta"]["hybrid_decision_type"] = override_reason
        
        return res
