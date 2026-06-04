# backend/app/main.py (updated section)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware import (
    ExceptionHandlerMiddleware,
    GlobalRateLimitMiddleware,
    RequestLoggerMiddleware,
    RequestIDMiddleware,
)
from app.api.v1.router import api_router
from app.config import settings

app = FastAPI(title="Salon Scheduler API", version="1.0.0")

# Add global exception handler first (catches all)
app.add_middleware(ExceptionHandlerMiddleware)

# Global rate limiter: 100 requests per minute per IP
app.add_middleware(GlobalRateLimitMiddleware, requests_per_minute=100)

# Add request ID middleware
app.add_middleware(RequestIDMiddleware)

# Add request logger
app.add_middleware(RequestLoggerMiddleware)

# CORS (should be after exception handler, but order with logging doesn't matter much)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Salon Scheduler API", "docs": "/docs"}