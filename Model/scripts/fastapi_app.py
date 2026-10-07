import sys
from pathlib import Path
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jobsafe import JobsafeHybridEngine

app = FastAPI(
    title="JOBSAFE Explainable Risk Engine API",
    description="Ordinal Recruitment Risk Assessment API (v3.0.0)",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

hybrid_engine = JobsafeHybridEngine()

class AnalyzeRequest(BaseModel):
    text: str = Field("", max_length=20000, description="Raw job posting text or OCR text output")
    url: Optional[str] = Field(None, description="Optional application URL")
    mode: Optional[str] = Field("hybrid", description="Engine mode: 'hybrid' | 'rule_only' | 'ml_only'")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "engine_version": hybrid_engine.rule_engine.config["version"],
        "ml_loaded": hybrid_engine.ml_model is not None,
        "supported_modes": ["hybrid", "rule_only", "ml_only"]
    }

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    """
    Evaluates recruitment text for fraud & exploitation risks.
    Complies with UU PDP No. 27/2022 (Zero logging of applicant inputs).
    """
    return hybrid_engine.analyze(req.text, req.url, mode=req.mode or "hybrid")
