from celery import shared_task
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.google_places_service import GooglePlacesService

@shared_task
def refresh_salon_cache():
    """Refresh salon data from Google Places for popular locations."""
    # List of popular locations to refresh
    locations = [
        {"lat": 40.7128, "lng": -74.0060, "radius": 5000},  # New York
        {"lat": 34.0522, "lng": -118.2437, "radius": 5000},  # Los Angeles
        {"lat": 41.8781, "lng": -87.6298, "radius": 5000},   # Chicago
    ]
    db = SessionLocal()
    try:
        for loc in locations:
            await GooglePlacesService.fetch_and_cache_salons(
                db, loc["lat"], loc["lng"], loc["radius"]
            )
        db.commit()
        return {"status": "completed", "locations_refreshed": len(locations)}
    finally:
        db.close()