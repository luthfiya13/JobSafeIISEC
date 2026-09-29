import sqlite3
import json
import os
import bcrypt
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.config import settings
from app.engine.indicators import DEFAULT_INDICATORS

def hash_password(password: str) -> str:
    pwd_bytes = password[:72].encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password[:72].encode("utf-8")
    return bcrypt.checkpw(pwd_bytes, hashed_password.encode("utf-8"))

DB_PATH = "jobsafe.db"

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Admin Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        name TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    # Analysis History table (anonymous user analysis logs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        input_type TEXT NOT NULL, -- 'text', 'photo', 'link'
        input_preview TEXT NOT NULL,
        risk_score INTEGER NOT NULL,
        risk_level TEXT NOT NULL,
        level_code TEXT NOT NULL,
        indicators_json TEXT NOT NULL,
        detected_count INTEGER NOT NULL,
        summary TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    # Custom Indicators table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS indicators_config (
        code TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        weight INTEGER NOT NULL,
        is_active INTEGER NOT NULL,
        description TEXT NOT NULL,
        why_important TEXT NOT NULL,
        keywords_json TEXT NOT NULL,
        patterns_json TEXT NOT NULL
    );
    """)

    # System Settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );
    """)

    # Seed Default Admin if not exists
    cursor.execute("SELECT id FROM admin_users WHERE email = ?", (settings.ADMIN_EMAIL,))
    if not cursor.fetchone():
        hashed = hash_password(settings.ADMIN_PASSWORD)
        cursor.execute(
            "INSERT INTO admin_users (email, hashed_password, name, created_at) VALUES (?, ?, ?, ?)",
            (settings.ADMIN_EMAIL, hashed, "Administrator JOBSAFE", datetime.now().isoformat())
        )

    # Seed Indicators if empty
    cursor.execute("SELECT COUNT(*) as cnt FROM indicators_config")
    if cursor.fetchone()["cnt"] == 0:
        for ind in DEFAULT_INDICATORS:
            cursor.execute("""
            INSERT INTO indicators_config (code, name, category, weight, is_active, description, why_important, keywords_json, patterns_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ind["code"],
                ind["name"],
                ind.get("category", "Umum"),
                ind["weight"],
                1 if ind.get("is_active", True) else 0,
                ind["description"],
                ind["why_important"],
                json.dumps(ind.get("keywords", [])),
                json.dumps(ind.get("patterns", []))
            ))

    # Seed default system settings
    default_settings = {
        "site_name": "JOBSAFE",
        "threshold_low_max": "29",
        "threshold_med_max": "69",
        "threshold_high_min": "70",
        "analysis_engine_version": "v2.6-standard",
        "maintenance_mode": "false"
    }
    for k, v in default_settings.items():
        cursor.execute("INSERT OR IGNORE INTO system_settings (key, value) VALUES (?, ?)", (k, v))

    # Pre-populate sample realistic analyses if history is empty (for rich prototype admin dashboard experience)
    cursor.execute("SELECT COUNT(*) as cnt FROM analysis_history")
    if cursor.fetchone()["cnt"] == 0:
        samples = [
            (
                "text",
                "Dicari Admin Online Like Video TikTok & YouTube. Komisi harian 500rb - 1jt. Wajib deposit awal Rp250.000 untuk buka akun tugas...",
                85,
                "RISIKO TINGGI",
                "HIGH",
                json.dumps([{"code": "R1", "name": "Biaya di Awal"}, {"code": "R2", "name": "Imbalan Tidak Wajar"}, {"code": "R6", "name": "Skema Tugas Berantai"}]),
                3,
                "Ditemukan indikator kuat skema tugas berantai like/subscribe dengan syarat deposit uang di awal.",
                "2026-09-27T14:20:00"
            ),
            (
                "link",
                "https://karir-bumn-rekrutmen.id/panggilan-interview-surat-resmi",
                75,
                "RISIKO TINGGI",
                "HIGH",
                json.dumps([{"code": "R7", "name": "Perjalanan/Akomodasi Wajib"}, {"code": "R4", "name": "Identitas Perusahaan Tidak Jelas"}]),
                2,
                "Mengarah pada modus penipuan panggilan tes luar kota dengan kewajiban reservasi tiket travel fiktif.",
                "2026-09-27T16:45:00"
            ),
            (
                "text",
                "Dibutuhkan Data Entry Remote Part Time. Kirimkan foto KTP depan belakang dan buku tabungan via WhatsApp admin...",
                55,
                "RISIKO SEDANG",
                "MEDIUM",
                json.dumps([{"code": "R3", "name": "Permintaan Dokumen Sensitif"}, {"code": "R8", "name": "Kanal Komunikasi Tidak Resmi"}]),
                2,
                "Permintaan dokumen identitas pribadi di tahap awal melalui WhatsApp tanpa saluran resmi korporat.",
                "2026-09-28T08:10:00"
            ),
            (
                "text",
                "Lowongan Frontend Engineer (React/Next.js) di PT Teknologi Maju Bersama. Penempatan Jakarta Selatan. Gaji kompetitif sesuai pengalaman.",
                10,
                "RISIKO RENDAH",
                "LOW",
                json.dumps([]),
                0,
                "Format dan kualifikasi lowongan terlihat standar dan profesional, tidak ditemukan tanda-tanda risiko signifikan.",
                "2026-09-28T08:50:00"
            )
        ]
        for s in samples:
            cursor.execute("""
            INSERT INTO analysis_history (input_type, input_preview, risk_score, risk_level, level_code, indicators_json, detected_count, summary, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, s)

    conn.commit()
    conn.close()

def get_all_indicators() -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM indicators_config ORDER BY code ASC")
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "code": r["code"],
            "name": r["name"],
            "category": r["category"],
            "weight": r["weight"],
            "is_active": bool(r["is_active"]),
            "description": r["description"],
            "why_important": r["why_important"],
            "keywords": json.loads(r["keywords_json"]),
            "patterns": json.loads(r["patterns_json"])
        })
    return result

def update_indicator(code: str, weight: int, is_active: bool, description: str) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE indicators_config 
    SET weight = ?, is_active = ?, description = ?
    WHERE code = ?
    """, (weight, 1 if is_active else 0, description, code))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0

def save_analysis_record(input_type: str, input_preview: str, risk_score: int, risk_level: str, level_code: str, indicators: list, detected_count: int, summary: str) -> int:
    conn = get_db()
    cursor = conn.cursor()
    now_iso = datetime.now().isoformat()
    cursor.execute("""
    INSERT INTO analysis_history (input_type, input_preview, risk_score, risk_level, level_code, indicators_json, detected_count, summary, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        input_type,
        input_preview[:180],
        risk_score,
        risk_level,
        level_code,
        json.dumps(indicators),
        detected_count,
        summary,
        now_iso
    ))
    conn.commit()
    rec_id = cursor.lastrowid
    conn.close()
    return rec_id
