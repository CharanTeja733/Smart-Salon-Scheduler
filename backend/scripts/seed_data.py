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

        # Default opening hours for practitioners
        DEFAULT_HOURS = {
            "monday": "09:00-18:00",
            "tuesday": "09:00-18:00",
            "wednesday": "09:00-18:00",
            "thursday": "09:00-18:00",
            "friday": "09:00-18:00",
            "saturday": "10:00-16:00",
            "sunday": "closed"
        }

        women_photos = [f"https://randomuser.me/api/portraits/women/{i}.jpg" for i in range(1, 80)]
        men_photos = [f"https://randomuser.me/api/portraits/men/{i}.jpg" for i in range(1, 80)]
        photo_index = 0

        # Define all practitioner roles (including the new service types)
        practitioner_templates = [
            {
                "name": "Senior Stylist",
                "specialty": "Haircut & Color",
                "experience_years": 8,
                "bio": "Specializes in modern cuts and balayage.",
                "base_price": 75.0,
                "lunch_break_start": time(13, 0),
                "lunch_break_end": time(14, 0),
                "off_days": ["sunday"],
                "specializations": ["haircut", "color", "blowout"],
                "service_prices": {"haircut": 75, "color": 150, "blowout": 50},
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
                "specializations": ["haircut", "blowout"],
                "service_prices": {"haircut": 45, "blowout": 35},
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
            {
                "name": "Blowout Specialist",
                "specialty": "Blowouts & Styling",
                "experience_years": 4,
                "bio": "Perfect blowouts and event styling.",
                "base_price": 60.0,
                "lunch_break_start": time(13, 0),
                "lunch_break_end": time(14, 0),
                "off_days": ["wednesday"],
                "specializations": ["blowout"],
                "service_prices": {"blowout": 60, "updo": 80},
                "gender": "women",
                "min_rating": 3.8,
                "max_rating": 4.9,
            },
            {
                "name": "Nail Technician",
                "specialty": "Nail Care",
                "experience_years": 3,
                "bio": "Manicures, pedicures, and gel nails.",
                "base_price": 40.0,
                "lunch_break_start": time(13, 0),
                "lunch_break_end": time(14, 0),
                "off_days": ["thursday"],
                "specializations": ["nails"],
                "service_prices": {"manicure": 40, "pedicure": 60, "gel": 50},
                "gender": "women",
                "min_rating": 3.5,
                "max_rating": 4.8,
            },
            {
                "name": "Makeup Artist",
                "specialty": "Makeup & Enhancements",
                "experience_years": 4,
                "bio": "Everyday and bridal makeup.",
                "base_price": 70.0,
                "lunch_break_start": time(13, 0),
                "lunch_break_end": time(14, 0),
                "off_days": ["friday"],
                "specializations": ["makeup"],
                "service_prices": {"basic": 70, "bridal": 200},
                "gender": "women",
                "min_rating": 4.0,
                "max_rating": 5.0,
            },
            {
                "name": "Waxing Specialist",
                "specialty": "Hair Removal",
                "experience_years": 2,
                "bio": "Gentle waxing for face and body.",
                "base_price": 30.0,
                "lunch_break_start": time(13, 0),
                "lunch_break_end": time(14, 0),
                "off_days": ["saturday"],
                "specializations": ["waxing"],
                "service_prices": {"eyebrow": 15, "full_face": 30, "full_body": 100},
                "gender": "women",
                "min_rating": 3.5,
                "max_rating": 4.7,
            },
            {
                "name": "Facial Specialist",
                "specialty": "Skin Care",
                "experience_years": 5,
                "bio": "Custom facials and skincare treatments.",
                "base_price": 80.0,
                "lunch_break_start": time(13, 0),
                "lunch_break_end": time(14, 0),
                "off_days": ["sunday"],
                "specializations": ["facial"],
                "service_prices": {"basic_facial": 80, "anti_aging": 120},
                "gender": "women",
                "min_rating": 4.0,
                "max_rating": 5.0,
            },
        ]

        for salon in salons[:10]:  # first 10 salons
            for template in practitioner_templates:
                name_part = template["name"].replace(" ", "_").lower()
                email = f"{name_part}_{salon.id}@example.com"

                existing = db.query(Practitioner).filter(Practitioner.email == email).first()
                if existing:
                    print(f"Practitioner {email} already exists, skipping.")
                    continue

                rating = round(random.uniform(template["min_rating"], template["max_rating"]), 1)

                if template["gender"] == "women":
                    photo_url = women_photos[photo_index % len(women_photos)]
                else:
                    photo_url = men_photos[photo_index % len(men_photos)]
                photo_index += 1

                practitioner = Practitioner(
                    salon_id=salon.id,
                    name=f"{template['name']} {salon.id}",
                    email=email,
                    phone="+1234567890",
                    specialty=template["specialty"],
                    experience_years=template["experience_years"],
                    bio=template["bio"],
                    photo_url=photo_url,
                    base_price=template["base_price"],
                    service_prices=template["service_prices"],
                    specializations=template["specializations"],
                    rating=rating,
                    total_reviews=random.randint(5, 100),
                    lunch_break_start=template["lunch_break_start"],
                    lunch_break_end=template["lunch_break_end"],
                    off_days=template["off_days"],
                    is_active=True,
                    default_opening_hours=DEFAULT_HOURS,
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