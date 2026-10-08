import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from app.database.db import get_db, get_all_indicators, update_indicator
from app.api.auth import verify_password, create_access_token, get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin Portal"])

class LoginRequest(BaseModel):
    email: str
    password: str

class IndicatorUpdateRequest(BaseModel):
    weight: int
    is_active: bool
    description: str

class SettingsUpdateRequest(BaseModel):
    site_name: Optional[str] = None
    threshold_low_max: Optional[int] = None
    threshold_med_max: Optional[int] = None
    threshold_high_min: Optional[int] = None
    maintenance_mode: Optional[bool] = None

@router.post("/login")
def admin_login(req: LoginRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, hashed_password, name FROM admin_users WHERE email = ?", (req.email.strip().lower(),))
    user = cursor.fetchone()
    conn.close()

    if not user or not verify_password(req.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau kata sandi admin tidak sesuai."
        )

    access_token = create_access_token(data={"sub": user["email"], "name": user["name"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "admin": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"]
        }
    }

@router.get("/me")
def get_current_admin_info(current_admin: dict = Depends(get_current_admin)):
    return current_admin

@router.get("/dashboard")
def get_dashboard_stats(current_admin: dict = Depends(get_current_admin)):
    conn = get_db()
    cursor = conn.cursor()

    # Total and counts by risk level
    cursor.execute("SELECT COUNT(*) as total FROM analysis_history")
    total_analyses = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as low_count FROM analysis_history WHERE level_code = 'LOW'")
    low_count = cursor.fetchone()["low_count"]

    cursor.execute("SELECT COUNT(*) as med_count FROM analysis_history WHERE level_code = 'MEDIUM'")
    med_count = cursor.fetchone()["med_count"]

    cursor.execute("SELECT COUNT(*) as high_count FROM analysis_history WHERE level_code = 'HIGH'")
    high_count = cursor.fetchone()["high_count"]

    # Recent 5 analyses
    cursor.execute("SELECT * FROM analysis_history ORDER BY id DESC LIMIT 5")
    recent_rows = cursor.fetchall()
    recent = []
    for r in recent_rows:
        recent.append({
            "id": r["id"],
            "input_type": r["input_type"],
            "input_preview": r["input_preview"],
            "risk_score": r["risk_score"],
            "risk_level": r["risk_level"],
            "level_code": r["level_code"],
            "detected_count": r["detected_count"],
            "created_at": r["created_at"]
        })

    # Indicator frequency count
    cursor.execute("SELECT indicators_json FROM analysis_history")
    all_history = cursor.fetchall()
    conn.close()

    freq: Dict[str, int] = {}
    for row in all_history:
        try:
            inds = json.loads(row["indicators_json"])
            for item in inds:
                code = item.get("code") or item.get("name")
                freq[code] = freq.get(code, 0) + 1
        except Exception:
            pass

    freq_list = sorted([{"code": k, "count": v} for k, v in freq.items()], key=lambda x: x["count"], reverse=True)

    return {
        "total_analyses": total_analyses,
        "risk_low": low_count,
        "risk_medium": med_count,
        "risk_high": high_count,
        "distribution": {
            "low_pct": round((low_count / total_analyses * 100) if total_analyses else 0, 1),
            "med_pct": round((med_count / total_analyses * 100) if total_analyses else 0, 1),
            "high_pct": round((high_count / total_analyses * 100) if total_analyses else 0, 1)
        },
        "top_indicators": freq_list[:6],
        "recent_analyses": recent
    }

@router.get("/analyses")
def list_analyses(
    q: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    limit: int = 50,
    offset: int = 0,
    current_admin: dict = Depends(get_current_admin)
):
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM analysis_history WHERE 1=1"
    params = []

    if q:
        query += " AND (input_preview LIKE ? OR summary LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%"])

    if level and level != "ALL":
        query += " AND level_code = ?"
        params.append(level.upper())

    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    items = []
    for r in rows:
        items.append({
            "id": r["id"],
            "input_type": r["input_type"],
            "input_preview": r["input_preview"],
            "risk_score": r["risk_score"],
            "risk_level": r["risk_level"],
            "level_code": r["level_code"],
            "indicators": json.loads(r["indicators_json"]),
            "detected_count": r["detected_count"],
            "summary": r["summary"],
            "created_at": r["created_at"]
        })

    return {"items": items, "count": len(items)}

@router.get("/reports")
def list_reports(current_admin: dict = Depends(get_current_admin)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, analysis_id, listing_text, complaint, created_at FROM user_reports ORDER BY id DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return {
        "items": [
            {
                "id": row["id"],
                "analysis_id": row["analysis_id"],
                "listing_preview": row["listing_text"],
                "complaint": row["complaint"],
                "created_at": row["created_at"],
            }
            for row in rows
        ],
        "count": len(rows),
    }

@router.get("/analyses/{id}")
def get_analysis_detail(id: int, current_admin: dict = Depends(get_current_admin)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analysis_history WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Data analisis tidak ditemukan.")

    return {
        "id": row["id"],
        "input_type": row["input_type"],
        "input_preview": row["input_preview"],
        "risk_score": row["risk_score"],
        "risk_level": row["risk_level"],
        "level_code": row["level_code"],
        "indicators": json.loads(row["indicators_json"]),
        "detected_count": row["detected_count"],
        "summary": row["summary"],
        "created_at": row["created_at"]
    }

@router.get("/indicators")
def get_indicators_list(current_admin: dict = Depends(get_current_admin)):
    indicators = get_all_indicators()
    total_weight = sum(ind["weight"] for ind in indicators if ind["is_active"])
    return {
        "indicators": indicators,
        "total_weight": total_weight,
        "is_valid_total": total_weight == 100
    }

@router.put("/indicators/{code}")
def update_indicator_config(
    code: str,
    req: IndicatorUpdateRequest,
    current_admin: dict = Depends(get_current_admin)
):
    success = update_indicator(
        code=code.upper(),
        weight=req.weight,
        is_active=req.is_active,
        description=req.description
    )
    if not success:
        raise HTTPException(status_code=404, detail="Indikator tidak ditemukan.")

    indicators = get_all_indicators()
    total_weight = sum(ind["weight"] for ind in indicators if ind["is_active"])

    return {
        "success": True,
        "message": f"Indikator {code} berhasil diperbarui.",
        "total_weight": total_weight,
        "is_valid_total": total_weight == 100
    }

@router.get("/settings")
def get_settings(current_admin: dict = Depends(get_current_admin)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM system_settings")
    rows = cursor.fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}

@router.put("/settings")
def update_settings(req: SettingsUpdateRequest, current_admin: dict = Depends(get_current_admin)):
    conn = get_db()
    cursor = conn.cursor()

    if req.site_name is not None:
        cursor.execute("UPDATE system_settings SET value = ? WHERE key = 'site_name'", (req.site_name,))
    if req.threshold_low_max is not None:
        cursor.execute("UPDATE system_settings SET value = ? WHERE key = 'threshold_low_max'", (str(req.threshold_low_max),))
    if req.threshold_med_max is not None:
        cursor.execute("UPDATE system_settings SET value = ? WHERE key = 'threshold_med_max'", (str(req.threshold_med_max),))
    if req.threshold_high_min is not None:
        cursor.execute("UPDATE system_settings SET value = ? WHERE key = 'threshold_high_min'", (str(req.threshold_high_min),))
    if req.maintenance_mode is not None:
        cursor.execute("UPDATE system_settings SET value = ? WHERE key = 'maintenance_mode'", (str(req.maintenance_mode).lower(),))

    conn.commit()
    conn.close()
    return {"success": True, "message": "Pengaturan sistem berhasil diperbarui."}
