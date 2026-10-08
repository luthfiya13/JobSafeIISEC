import os

class Settings:
    PROJECT_NAME: str = "JOBSAFE"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Admin Default Account
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "")

    # Risk Thresholds
    THRESHOLD_LOW_MAX: int = 29
    THRESHOLD_MED_MAX: int = 69
    THRESHOLD_HIGH_MIN: int = 70

    # Database
    DATABASE_URL: str = "sqlite:///./jobsafe.db"

settings = Settings()
