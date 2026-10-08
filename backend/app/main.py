from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.db import init_db, get_all_indicators
from app.api.analyze import router as analyze_router
from app.api.admin import router as admin_router
from app.api.reports import router as reports_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="JOBSAFE API - Digital Job Risk Assessment Platform",
    version="1.0.0"
)

# Enable CORS for Next.js frontend (default port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def root():
    return {
        "app": "JOBSAFE API",
        "status": "online",
        "version": "1.0.0",
        "description": "Platform Penilaian Risiko Lowongan Kerja Digital"
    }

@app.get("/health")
def health():
    return {"status": "ok", "service": "jobsafe-api"}

@app.get("/api/public-indicators")
def get_public_indicators():
    """Public indicator reference for visitor landing/info page"""
    inds = get_all_indicators()
    return [
        {
            "code": i["code"],
            "name": i["name"],
            "category": i["category"],
            "weight": i["weight"],
            "description": i["description"],
            "why_important": i["why_important"]
        }
        for i in inds if i["is_active"]
    ]

# Include routers
app.include_router(analyze_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
