from fastapi import APIRouter

from app.api.v1 import (
    ai,
    appointments,
    customers,
    practitioners,
    reviews,
    salons,
    waitlist,
    webhooks,
)

api_router = APIRouter(prefix="/api/v1")

# Health check
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Include all sub-routers
api_router.include_router(salons.router, prefix="/salons", tags=["Salons"])
api_router.include_router(practitioners.router, prefix="/practitioners", tags=["Practitioners"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(waitlist.router, prefix="/waitlist", tags=["Waitlist"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Features"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
