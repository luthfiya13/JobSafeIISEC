from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.engine.analyzer import RiskAnalyzer
from app.engine.scraper_service import scrape_job_url
from app.engine.ocr_service import extract_text_from_image
from app.database.db import get_all_indicators, save_analysis_record

router = APIRouter(prefix="/analyze", tags=["Risk Analysis"])

class TextAnalysisRequest(BaseModel):
    text: str

class UrlAnalysisRequest(BaseModel):
    url: str

@router.post("/text")
def analyze_text_endpoint(req: TextAnalysisRequest):
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(
            status_code=400,
            detail="Teks lowongan belum diisi. Silakan tempel teks deskripsi lowongan kerja."
        )
    if len(text) < 15:
        raise HTTPException(
            status_code=400,
            detail="Teks lowongan terlalu pendek. Masukkan minimal 15 karakter untuk analisis yang memadai."
        )

    # Load active indicators from DB
    indicators = get_all_indicators()
    analyzer = RiskAnalyzer(indicators=indicators)

    result = analyzer.analyze(text)

    # Save anonymous summary for admin statistics
    detected_list = [
        {"code": ind["code"], "name": ind["name"]}
        for ind in result["indicators"]
        if ind["status"] in ["RISIKO_TINGGI", "PERLU_PERHATIAN"]
    ]

    record_id = save_analysis_record(
        input_type="text",
        input_preview=text[:160],
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        level_code=result["level_code"],
        indicators=detected_list,
        detected_count=result["indicators_detected_count"],
        summary=result["summary"]
    )
    result["id"] = record_id
    result["raw_input"] = text
    result["input_type"] = "text"

    return result

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
    indicators = get_all_indicators()
    analyzer = RiskAnalyzer(indicators=indicators)
    result = analyzer.analyze(extracted_text)

    detected_list = [
        {"code": ind["code"], "name": ind["name"]}
        for ind in result["indicators"]
        if ind["status"] in ["RISIKO_TINGGI", "PERLU_PERHATIAN"]
    ]

    record_id = save_analysis_record(
        input_type="link",
        input_preview=url,
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        level_code=result["level_code"],
        indicators=detected_list,
        detected_count=result["indicators_detected_count"],
        summary=result["summary"]
    )
    result["id"] = record_id
    result["raw_input"] = url
    result["extracted_text"] = extracted_text
    result["page_title"] = scrape_res.get("title", "")
    result["input_type"] = "link"

    return result

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
    elif fallback_text and len(fallback_text.strip()) >= 15:
        extracted_text = fallback_text.strip()
    else:
        raise HTTPException(
            status_code=400,
            detail=ocr_res.get("error", "Teks dalam foto belum dapat dibaca secara jelas. Silakan salin teks ke tab Teks.")
        )

    indicators = get_all_indicators()
    analyzer = RiskAnalyzer(indicators=indicators)
    result = analyzer.analyze(extracted_text)

    detected_list = [
        {"code": ind["code"], "name": ind["name"]}
        for ind in result["indicators"]
        if ind["status"] in ["RISIKO_TINGGI", "PERLU_PERHATIAN"]
    ]

    record_id = save_analysis_record(
        input_type="photo",
        input_preview=f"Foto: {file.filename} ({len(content)} bytes)",
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        level_code=result["level_code"],
        indicators=detected_list,
        detected_count=result["indicators_detected_count"],
        summary=result["summary"]
    )
    result["id"] = record_id
    result["raw_input"] = f"Unggahan Foto: {file.filename}"
    result["extracted_text"] = extracted_text
    result["input_type"] = "photo"

    return result
