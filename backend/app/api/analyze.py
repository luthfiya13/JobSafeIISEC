from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.engine.jobsafe_service import get_jobsafe_service
from app.engine.scraper_service import scrape_job_url
from app.engine.ocr_service import extract_text_from_image
from app.database.db import get_all_indicators, save_analysis_record

router = APIRouter(prefix="/analyze", tags=["Risk Analysis"])

class TextAnalysisRequest(BaseModel):
    text: str

class UrlAnalysisRequest(BaseModel):
    url: str


def _run_analysis(text: str, input_type: str, raw_input: str, extra: Optional[Dict[str, Any]] = None):
    result = get_jobsafe_service().analyze(text, indicators=get_all_indicators())
    detected_list = [
        {"code": ind["code"], "name": ind["name"]}
        for ind in result["indicators"]
        if ind["status"] in ["RISIKO_TINGGI", "PERLU_PERHATIAN"]
    ]
    record_id = save_analysis_record(
        input_type=input_type,
        input_preview=raw_input,
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        level_code=result["level_code"],
        indicators=detected_list,
        detected_count=result["indicators_detected_count"],
        summary=result["summary"],
    )
    result.update({"id": record_id, "raw_input": raw_input, "input_type": input_type})
    if extra:
        result.update(extra)
    return result

@router.post("/text")
def analyze_text_endpoint(req: TextAnalysisRequest):
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(
            status_code=400,
            detail="Teks lowongan belum diisi. Silakan tempel teks deskripsi lowongan kerja."
        )
    if len(text) < 20:
        raise HTTPException(
            status_code=400,
            detail="Teks lowongan terlalu pendek. Masukkan minimal 20 karakter untuk analisis yang memadai."
        )

    # Load active indicators from DB
    return _run_analysis(text, "text", text[:160])

@router.post("/url")
def analyze_url_endpoint(req: UrlAnalysisRequest):
    url = (req.url or "").strip()
    if not url:
        raise HTTPException(
            status_code=400,
            detail="Tautan lowongan belum diisi. Masukkan URL lowongan yang ingin diperiksa."
        )

    scrape_res = scrape_job_url(url)
    if not scrape_res.get("success"):
        raise HTTPException(
            status_code=400,
            detail=scrape_res.get("error", "Kami belum dapat mengakses tautan ini. Silakan tempel teks secara manual.")
        )

    extracted_text = scrape_res["text"]
    return _run_analysis(extracted_text, "link", url, {"extracted_text": extracted_text, "page_title": scrape_res.get("title", "")})

@router.post("/photo")
async def analyze_photo_endpoint(
    file: UploadFile = File(...),
    fallback_text: Optional[str] = Form(None)
):
    if not file:
        raise HTTPException(status_code=400, detail="Berkas foto belum dipilih.")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Ukuran foto melebihi batas 10MB.")

    extracted_text = ""
    ocr_res = extract_text_from_image(content)
    if ocr_res.get("success"):
        extracted_text = ocr_res["text"]
    elif fallback_text and len(fallback_text.strip()) >= 20:
        extracted_text = fallback_text.strip()
    else:
        raise HTTPException(
            status_code=400,
            detail=ocr_res.get("error", "Teks dalam foto belum dapat dibaca secara jelas. Silakan salin teks ke tab Teks.")
        )

    return _run_analysis(extracted_text, "photo", f"Unggahan Foto: {file.filename}", {"extracted_text": extracted_text})
