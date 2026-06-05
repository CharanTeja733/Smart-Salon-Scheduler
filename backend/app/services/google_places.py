from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.repositories import SalonRepository


class GooglePlacesService:
    BASE_URL = "https://maps.googleapis.com/maps/api/place"

    @staticmethod
    async def search_nearby(lat: float, lng: float, radius: int = 5000, keyword: str = "salon"):
        async with httpx.AsyncClient() as client:
            params = {
                "location": f"{lat},{lng}",
                "radius": radius,
                "keyword": keyword,
                "key": settings.GOOGLE_PLACES_API_KEY
            }
            response = await client.get(f"{GooglePlacesService.BASE_URL}/nearbysearch/json", params=params)
            response.raise_for_status()
            return response.json().get("results", [])

    @staticmethod
    async def get_place_details(place_id: str):
        async with httpx.AsyncClient() as client:
            params = {
                "place_id": place_id,
                "fields": "name,formatted_address,geometry,rating,reviews,opening_hours,photo,international_phone_number",
                "key": settings.GOOGLE_PLACES_API_KEY
            }
            response = await client.get(f"{GooglePlacesService.BASE_URL}/details/json", params=params)
            response.raise_for_status()
            return response.json().get("result", {})

    @staticmethod
    async def fetch_and_cache_salons(db: Session, lat: float, lng: float, radius: int = 5000):
        results = await GooglePlacesService.search_nearby(lat, lng, radius)
        salon_repo = SalonRepository()
        for place in results:
            salon_data = {
                "google_place_id": place["place_id"],
                "name": place["name"],
                "address": place.get("vicinity", ""),
                "latitude": place["geometry"]["location"]["lat"],
                "longitude": place["geometry"]["location"]["lng"],
                "rating": place.get("rating", 0.0),
                "rating_count": place.get("user_ratings_total", 0),
                "opening_hours": place.get("opening_hours", {}).get("weekday_text", []),
                "photo_reference": place.get("photos", [{}])[0].get("photo_reference"),
                "cached_at": datetime.utcnow()
            }
            salon_repo.upsert_from_google(db, salon_data)
        db.commit()
