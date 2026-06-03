# backend/app/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App metadata
    APP_NAME: str = "Salon Scheduler API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production

    # Database & Redis (loaded from .env)
    DATABASE_URL: str
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # External APIs
    GOOGLE_PLACES_API_KEY: str
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str
    RESEND_API_KEY: str

    # Business rules (defaults – can be overridden by .env)
    BOOKING_MIN_ADVANCE_HOURS: int = 1
    BOOKING_MAX_ADVANCE_DAYS: int = 90
    BOOKING_HOLD_MINUTES: int = 10
    DEPOSIT_PERCENTAGE: float = 20.0

    # Rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100

    # Caching
    SALON_CACHE_TTL_SECONDS: int = 604800  # 7 days

    # Security (if you add auth later)
    SECRET_KEY: str = "change-this-in-production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()