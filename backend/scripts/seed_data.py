import sys
import random
sys.path.insert(0, '/app')

from datetime import time
from app.database import SessionLocal
from app.models.practitioner import Practitioner
from app.models.salon import Salon

def seed_practitioners():
    db = SessionLocal()
    try:
        salons = db.query(Salon).all()
        if not salons:
            print("No salons found. Please import salons first.")
            return

        # Define default opening hours for practitioners (same as salon default)
        DEFAULT_HOURS = {
            "monday": "09:00-18:00",
            "tuesday": "09:00-18:00",
            "wednesday": "09:00-18:00",
            "thursday": "09:00-18:00",
            "friday": "09:00-18:00",
            "saturday": "10:00-16:00",
            "sunday": "closed"
        }

        women_photos = [f"https://randomuser.me/api/portraits/women/{i}.jpg" for i in range(1, 50)]
        men_photos = [f"https://randomuser.me/api/portraits/men/{i}.jpg" for i in range(1, 50)]
        photo_index = 0

        for salon in salons[:10]:
            practitioners_data = [
                {
                    "name": "Senior Stylist",
                    "specialty": "Haircut & Color",
                    "experience_years": 8,
                    "bio": "Specializes in modern cuts and balayage.",
                    "base_price": 75.0,
                    "lunch_break_start": time(13, 0),
                    "lunch_break_end": time(14, 0),
                    "off_days": ["sunday"],
                    "specializations": ["haircut", "color"],
                    "service_prices": {"haircut": 75, "color": 150},
                    "gender": "women",
                    "min_rating": 4.0,
                    "max_rating": 5.0,
                },
                {
                    "name": "Junior Stylist",
                    "specialty": "Men's Grooming",
                    "experience_years": 3,
                    "bio": "Expert in fades and beard trims.",
                    "base_price": 45.0,
                    "lunch_break_start": time(13, 0),
                    "lunch_break_end": time(14, 0),
                    "off_days": ["tuesday"],
                    "specializations": ["haircut"],
                    "service_prices": {"haircut": 45},
                    "gender": "men",
                    "min_rating": 3.0,
                    "max_rating": 4.5,
                },
                {
                    "name": "Color Specialist",
                    "specialty": "Color & Highlights",
                    "experience_years": 5,
                    "bio": "Creative color transformations.",
                    "base_price": 90.0,
                    "lunch_break_start": time(13, 0),
                    "lunch_break_end": time(14, 0),
                    "off_days": ["monday"],
                    "specializations": ["color", "balayage"],
                    "service_prices": {"color": 150, "balayage": 200},
                    "gender": "women",
                    "min_rating": 4.0,
                    "max_rating": 5.0,
                },
            ]

            for data in practitioners_data:
                name_part = data["name"].replace(" ", "_").lower()
                email = f"{name_part}_{salon.id}@example.com"

                existing = db.query(Practitioner).filter(Practitioner.email == email).first()
                if existing:
                    print(f"Practitioner {email} already exists, skipping.")
                    continue

                rating = round(random.uniform(data["min_rating"], data["max_rating"]), 1)

                if data["gender"] == "women":
                    photo_url = women_photos[photo_index % len(women_photos)]
                else:
                    photo_url = men_photos[photo_index % len(men_photos)]
                photo_index += 1

                practitioner = Practitioner(
                    salon_id=salon.id,
                    name=f"{data['name']} {salon.id}",
                    email=email,
                    phone="+1234567890",
                    specialty=data["specialty"],
                    experience_years=data["experience_years"],
                    bio=data["bio"],
                    photo_url=photo_url,
                    base_price=data["base_price"],
                    service_prices=data["service_prices"],
                    specializations=data["specializations"],
                    rating=rating,
                    total_reviews=random.randint(5, 100),
                    lunch_break_start=data["lunch_break_start"],
                    lunch_break_end=data["lunch_break_end"],
                    off_days=data["off_days"],
                    is_active=True,
                    default_opening_hours=DEFAULT_HOURS,   # <-- ADD THIS
                )
                db.add(practitioner)

            print(f"Added practitioners for salon: {salon.name}")

        db.commit()
        print("✅ Seed completed.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_practitioners()