from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.database.db import save_report

router = APIRouter(prefix="/reports", tags=["Reports"])


class ReportRequest(BaseModel):
    analysis_id: Optional[int] = None
    listing_text: str = Field(min_length=1, max_length=5000)
    complaint: str = Field(min_length=10, max_length=2000)


@router.post("")
def create_report(req: ReportRequest):
    report_id = save_report(req.analysis_id, req.listing_text, req.complaint)
    return {"success": True, "report_id": report_id, "message": "Aduan berhasil disimpan."}
