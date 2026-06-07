from datetime import datetime, timezone
from typing import Optional, List, Dict
import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.repositories import SalonRepository
from geoalchemy2.functions import ST_GeogFromText

class GooglePlacesService:
    BASE_URL = "https://maps.googleapis.com/maps/api/place"
    TIMEOUT_SECONDS = 5.0

    # ============ ASYNC VERSIONS (for FastAPI) ============

    @staticmethod
    async def search_nearby(lat: float, lng: float, radius: int = 5000, keyword: str = "salon") -> Optional[List[Dict]]:
        async with httpx.AsyncClient(timeout=GooglePlacesService.TIMEOUT_SECONDS) as client:
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
        async with httpx.AsyncClient(timeout=GooglePlacesService.TIMEOUT_SECONDS) as client:
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
        GooglePlacesService.store_results(db, results, lat, lng, radius)

    @staticmethod
    async def store_results(db: Session, results: List[Dict], lat: float, lng: float, radius: int):
        """Store Google Places results into salons table (async version)."""
        salon_repo = SalonRepository()
        if not results:
            key = f"no_results_{lat}_{lng}_{radius}"
            existing = salon_repo.get_by_google_place_id(db, key)
            if not existing:
                salon_repo.create(
                    db,
                    google_place_id=key,
                    name=f"No results for lat={lat} lng={lng} radius={radius}",
                    address="",
                    latitude=lat,
                    longitude=lng,
                    rating=0.0,
                    rating_count=0,
                    opening_hours={},
                    cached_at=datetime.utcnow()
                )
            else:
                existing.cached_at = datetime.utcnow()
                db.flush()
            return

        for place in results:
            # Build geography point
            lng = place["geometry"]["location"]["lng"]
            lat = place["geometry"]["location"]["lat"]
            point_text = f'POINT({lng} {lat})'

            # Inside _store_results_sync, after getting weekday_text
            weekday_text = place.get("opening_hours", {}).get("weekday_text", [])
            if weekday_text:
                # Convert list to dict (as before)
                opening_hours_dict = {}
                for line in weekday_text:
                    if ':' in line:
                        day, hours = line.split(':', 1)
                        opening_hours_dict[day.strip().lower()] = hours.strip()
            else:
                # Default hours (e.g., Mon-Fri 9-6, Sat 10-4, Sun closed)
                opening_hours_dict = {
                    "monday": "09:00-18:00",
                    "tuesday": "09:00-18:00",
                    "wednesday": "09:00-18:00",
                    "thursday": "09:00-18:00",
                    "friday": "09:00-18:00",
                    "saturday": "10:00-16:00",
                    "sunday": "closed"
                }

            location_value = ST_GeogFromText(point_text, srid=4326)
            salon_data = {
                "google_place_id": place["place_id"],
                "name": place["name"],
                "address": place.get("vicinity", ""),
                "latitude": place["geometry"]["location"]["lat"],
                "longitude": place["geometry"]["location"]["lng"],
                "phone": place.get("international_phone_number", None),
                "rating": place.get("rating", 0.0),
                "rating_count": place.get("user_ratings_total", 0),
                "opening_hours": opening_hours_dict,
                "photo_reference": place.get("photos", [{}])[0].get("photo_reference"),
                "cached_at": datetime.now(timezone.utc),
                "location": location_value
            }
            salon_repo.upsert_from_google(db, salon_data)
        db.commit()

    # ============ SYNC VERSIONS (for Celery tasks) ============

    @staticmethod
    def search_nearby_sync(lat: float, lng: float, radius: int = 5000, keyword: str = "salon") -> Optional[List[Dict]]:
        try:
            with httpx.Client(timeout=GooglePlacesService.TIMEOUT_SECONDS) as client:
                params = {
                    "location": f"{lat},{lng}",
                    "radius": radius,
                    "keyword": keyword,
                    "key": settings.GOOGLE_PLACES_API_KEY
                }
                response = client.get(f"{GooglePlacesService.BASE_URL}/nearbysearch/json", params=params)
                response.raise_for_status()
                data = response.json()
                return data.get("results", [])
        except (httpx.TimeoutException, httpx.HTTPStatusError, httpx.RequestError):
            return None

    @staticmethod
    def fetch_and_cache_salons_sync(db: Session, lat: float, lng: float, radius: int = 5000):
        results = GooglePlacesService.search_nearby_sync(lat, lng, radius)
        GooglePlacesService.store_results_sync(db, results, lat, lng, radius)

    @staticmethod
    def store_results_sync(db: Session, results: List[Dict], lat: float, lng: float, radius: int):
        """Store Google Places results into salons table (sync version for Celery)."""
        salon_repo = SalonRepository()
        if not results:
            key = f"no_results_{lat}_{lng}_{radius}"
            existing = salon_repo.get_by_google_place_id(db, key)
            if not existing:
                salon_repo.create(
                    db,
                    google_place_id=key,
                    name=f"No results for lat={lat} lng={lng} radius={radius}",
                    address="",
                    latitude=lat,
                    longitude=lng,
                    rating=0.0,
                    rating_count=0,
                    opening_hours={},
                    cached_at=datetime.utcnow()
                )
            else:
                existing.cached_at = datetime.utcnow()
                db.flush()
            return

        for place in results:
            # Build geography point
            lng = place["geometry"]["location"]["lng"]
            lat = place["geometry"]["location"]["lat"]
            point_text = f'POINT({lng} {lat})'

            # Inside _store_results_sync, after getting weekday_text
            weekday_text = place.get("opening_hours", {}).get("weekday_text", [])
            if weekday_text:
                # Convert list to dict (as before)
                opening_hours_dict = {}
                for line in weekday_text:
                    if ':' in line:
                        day, hours = line.split(':', 1)
                        opening_hours_dict[day.strip().lower()] = hours.strip()
            else:
                # Default hours (e.g., Mon-Fri 9-6, Sat 10-4, Sun closed)
                opening_hours_dict = {
                    "monday": "09:00-18:00",
                    "tuesday": "09:00-18:00",
                    "wednesday": "09:00-18:00",
                    "thursday": "09:00-18:00",
                    "friday": "09:00-18:00",
                    "saturday": "10:00-16:00",
                    "sunday": "closed"
                }

            location_value = ST_GeogFromText(point_text, srid=4326)
            salon_data = {
                "google_place_id": place["place_id"],
                "name": place["name"],
                "address": place.get("vicinity", ""),
                "latitude": place["geometry"]["location"]["lat"],
                "longitude": place["geometry"]["location"]["lng"],
                "phone": place.get("international_phone_number", None),
                "rating": place.get("rating", 0.0),
                "rating_count": place.get("user_ratings_total", 0),
                "opening_hours": opening_hours_dict,
                "photo_reference": place.get("photos", [{}])[0].get("photo_reference"),
                "cached_at": datetime.now(timezone.utc),
                "location": location_value
            }
            salon_repo.upsert_from_google(db, salon_data)
        db.commit()