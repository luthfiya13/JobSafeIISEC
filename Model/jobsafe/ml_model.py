from __future__ import annotations
import re
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import StandardScaler
from .text_utils import normalize_text, extract_entities

CLASSES = ["LOW", "MEDIUM", "HIGH"]

class JobsafeFeatureExtractor:
    """
    Multimodal Text & Structural Feature Extractor for JOBSAFE ML.
    Extracts:
    1. Word-level TF-IDF (1-2 grams)
    2. Character-level TF-IDF (3-5 grams)
    3. Structural & Lexical metadata (length, casing, entities, currency indicators)
    """
    def __init__(self, max_word_features: int = 2500, max_char_features: int = 3500):
        self.word_vec = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=max_word_features,
            sublinear_tf=True,
            strip_accents="unicode"
        )
        self.char_vec = TfidfVectorizer(
            analyzer="char",
            ngram_range=(3, 5),
            max_features=max_char_features,
            sublinear_tf=True
        )
        self.scaler = StandardScaler()
        self.fitted = False

    def _extract_dense_features(self, texts: List[str]) -> np.ndarray:
        feats = []
        for raw in texts:
            t = normalize_text(raw)
            ent = extract_entities(t)
            
            n_chars = len(t)
            n_words = len(t.split())
            upper_ratio = sum(1 for c in t if c.isupper()) / max(1, n_chars)
            digit_ratio = sum(1 for c in t if c.isdigit()) / max(1, n_chars)
            
            has_url = 1.0 if ent["urls"] else 0.0
            has_email = 1.0 if ent["emails"] else 0.0
            has_phone = 1.0 if ent["phones"] else 0.0
            has_foreign_phone = 1.0 if ent["foreign_phones"] else 0.0
            
            has_currency = 1.0 if re.search(r"\b(?:rp|usd|\$|juta|jt|ribu|rb)\b", t, re.I) else 0.0
            has_payment_word = 1.0 if re.search(r"\b(?:transfer|biaya|deposit|setor|bayar|top.?up)\b", t, re.I) else 0.0
            has_urgent_word = 1.0 if re.search(r"\b(?:kuota|terbatas|sekarang|buruan|langsung)\b", t, re.I) else 0.0
            
            feats.append([
                float(n_chars),
                float(n_words),
                upper_ratio,
                digit_ratio,
                has_url,
                has_email,
                has_phone,
                has_foreign_phone,
                has_currency,
                has_payment_word,
                has_urgent_word
            ])
        return np.array(feats, dtype=float)

    def fit(self, texts: List[str]):
        clean_texts = [normalize_text(t) for t in texts]
        self.word_vec.fit(clean_texts)
        self.char_vec.fit(clean_texts)
        dense = self._extract_dense_features(texts)
        self.scaler.fit(dense)
        self.fitted = True
        return self

    def transform(self, texts: List[str]):
        if not self.fitted:
            raise RuntimeError("FeatureExtractor must be fitted before calling transform().")
        clean_texts = [normalize_text(t) for t in texts]
        w_mat = self.word_vec.transform(clean_texts)
        c_mat = self.char_vec.transform(clean_texts)
        d_mat = self.scaler.transform(self._extract_dense_features(texts))
        return hstack([w_mat, c_mat, d_mat], format="csr")

    def fit_transform(self, texts: List[str]):
        return self.fit(texts).transform(texts)


class JobsafeMLModel:
    """
    Defensible Ordinal Recruitment Risk Classifier.
    Employs regularized Logistic Regression / Calibrated Linear Model.
    """
    def __init__(self, c_reg: float = 1.0, max_iter: int = 1000):
        self.c_reg = c_reg
        self.max_iter = max_iter
        self.featurizer = JobsafeFeatureExtractor()
        self.base_clf = LogisticRegression(
            C=c_reg,
            max_iter=max_iter,
            class_weight="balanced",
            random_state=42
        )
        self.calibrated_clf: Optional[CalibratedClassifierCV] = None
        self.classes_ = np.array(CLASSES)
        self.is_fitted = False

    def fit(self, texts: List[str], labels: List[str], calibrate: bool = True):
        y = np.array(labels)
        X = self.featurizer.fit_transform(texts)
        
        # Verify classes
        present_classes = np.unique(y)
        if len(present_classes) < 2:
            raise ValueError(f"Training requires at least 2 distinct classes, found: {present_classes}")
            
        if calibrate and len(present_classes) >= 3 and len(texts) >= 15:
            # Calibrate probabilities with 3-fold cross-validation
            cv_folds = min(3, min(np.bincount([CLASSES.index(cls) if cls in CLASSES else 0 for cls in y])))
            if cv_folds >= 2:
                self.calibrated_clf = CalibratedClassifierCV(self.base_clf, cv=cv_folds)
                self.calibrated_clf.fit(X, y)
                self.is_fitted = True
                return self

        self.base_clf.fit(X, y)
        self.calibrated_clf = None
        self.is_fitted = True
        return self

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("ML Model must be fitted before prediction.")
        X = self.featurizer.transform(texts)
        if self.calibrated_clf is not None:
            raw_proba = self.calibrated_clf.predict_proba(X)
            clf_classes = list(self.calibrated_clf.classes_)
        else:
            raw_proba = self.base_clf.predict_proba(X)
            clf_classes = list(self.base_clf.classes_)
            
        # Re-align probabilities to standard CLASSES order ["LOW", "MEDIUM", "HIGH"]
        aligned = np.zeros((len(texts), len(CLASSES)), dtype=float)
        for idx, cls_name in enumerate(CLASSES):
            if cls_name in clf_classes:
                src_idx = clf_classes.index(cls_name)
                aligned[:, idx] = raw_proba[:, src_idx]
        return aligned

    def predict(self, texts: List[str]) -> List[str]:
        proba = self.predict_proba(texts)
        pred_indices = np.argmax(proba, axis=1)
        return [CLASSES[i] for i in pred_indices]

    def predict_single(self, text: str) -> Dict[str, Any]:
        proba = self.predict_proba([text])[0]
        pred_idx = int(np.argmax(proba))
        pred_label = CLASSES[pred_idx]
        
        # Calculate continuous ML risk score (0 to 100)
        # LOW=0, MEDIUM=50, HIGH=100 expectation
        score = int(round(proba[0] * 5 + proba[1] * 45 + proba[2] * 90))
        
        return {
            "ml_predicted_level": pred_label,
            "ml_risk_score": score,
            "class_probabilities": {
                "LOW": round(float(proba[0]), 4),
                "MEDIUM": round(float(proba[1]), 4),
                "HIGH": round(float(proba[2]), 4)
            }
        }

    def save(self, model_path: Union[str, Path]):
        p = Path(model_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, model_path: Union[str, Path]) -> "JobsafeMLModel":
        with open(model_path, "rb") as f:
            return pickle.load(f)
