# Salon Scheduler – Backend + Frontend

A complete **intelligent appointment scheduling system** for a salon network, built for the ZySec Tech Hackathon 2026.  
Customers can search real salons (via Google Places), view practitioner profiles, book 30‑minute slots, pay a deposit (Stripe), receive SMS/email reminders, cancel with time‑based refunds, join waitlists, and review stylists. The system prevents double‑booking, handles practitioner availability (lunch breaks, off‑days, sick days), and includes AI‑powered stylist matching.

---

## 📁 Repository Structure

```
salon-scheduler/
├── backend/               # FastAPI Python backend
│   ├── app/               # Application code (models, services, API, tasks)
│   ├── migrations/        # Alembic database migrations
│   ├── requirements.txt   # Production dependencies
│   └── Dockerfile
├── frontend/              # React + Vite frontend
│   ├── src/               # Components, pages, services
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml     # Multi‑container setup
├── .env.example           # Environment variables template
├── init-db.sql            # PostGIS extension initialisation
└── README.md
```

---

## 🚀 Technologies Used

### Backend
- **FastAPI** – async web framework
- **PostgreSQL + PostGIS** – relational database with spatial queries
- **SQLAlchemy** – ORM
- **Alembic** – database migrations
- **Celery + Redis** – background tasks (reminders, cleanup)
- **Stripe** – deposit payments & refunds
- **Twilio** – SMS notifications
- **Resend** – email notifications
- **Google Places API** – real salon data
- **TextBlob** – review sentiment analysis

### Frontend
- **React 18** + Vite
- **React Router DOM** – client‑side routing
- **Tailwind CSS** – styling
- **Axios** – API client
- **Stripe Elements** – payment form
- **@react-google-maps/api** – interactive map

### DevOps
- **Docker** & Docker Compose – containerised development & deployment

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Salon search** | Real‑time search by location (lat/lng) with Google Places caching |
| **Practitioner availability** | 30‑minute slots, lunch breaks, recurring off‑days, sick day exceptions |
| **Double‑booking prevention** | Database row‑level locks + status checks |
| **Booking with deposit** | 20% deposit via Stripe, 10‑minute hold |
| **Cancellation & refund** | Time‑based policy (>24h → 100%, 2‑24h → 50%, <2h → 0%) |
| **Rescheduling** | Atomic swap of time slots |
| **Waitlist** | Auto‑notify customers when a slot opens |
| **AI stylist matching** | Weighted scoring (expertise, rating, sentiment, workload, distance, customer history) |
| **Reviews & sentiment** | Customer reviews with TextBlob sentiment analysis |
| **Notifications** | SMS (Twilio) + email (Resend) for confirmations, reminders, cancellations |
| **Webhook** | Stripe `payment_intent.succeeded` handles deposit confirmation |
| **Google Maps** | Interactive map with salon markers |
| **My Bookings** | View, cancel, reschedule, write reviews |
| **Waitlist view** | See your active waitlist entries with position |

---

## 🧩 API Endpoints (Selected)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/salons` | Search salons by location (returns `distance_meters`) |
| GET | `/salons/{id}` | Salon details + practitioners |
| GET | `/practitioners/{id}` | Practitioner profile (including reviews) |
| GET | `/practitioners/{id}/availability` | Available 30‑min slots for a date |
| POST | `/appointments` | Create booking (requires `Idempotency-Key`) |
| POST | `/appointments/{id}/confirm` | Confirm after successful Stripe payment |
| POST | `/appointments/{id}/cancel` | Cancel with refund |
| POST | `/appointments/{id}/reschedule` | Change appointment time |
| GET | `/customers/{phone}/appointments` | Customer’s bookings |
| POST | `/reviews` | Submit review (with sentiment analysis) |
| GET | `/ai/match-stylist` | AI stylist recommendations |
| POST | `/waitlist` | Join waitlist |
| GET | `/waitlist/` | Get waitlist entries by phone |

Full interactive documentation available at `http://localhost:8000/docs` (Swagger UI).

---

## 🔧 Setup Instructions (Local Development)

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (optional, for frontend outside Docker)
- Stripe CLI (optional, for testing webhooks)

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/salon-scheduler.git
cd salon-scheduler
```

### 2. Environment variables
Copy `.env.example` to `.env` in the project root and fill in your keys:

```bash
cp .env.example .env
```

Required keys:
- `GOOGLE_PLACES_API_KEY`
- `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
- `RESEND_API_KEY`
- `SECRET_KEY` (any random string for JWT)

### 3. Build and run with Docker Compose
```bash
docker compose up -d --build
```

This starts:
- PostgreSQL (PostGIS enabled) on port 5432
- Redis on port 6379
- FastAPI backend on port 8000
- Celery worker & beat
- React frontend on port 3000
- Adminer (database GUI) on port 8080

### 4. Run database migrations (Alembic)
```bash
docker compose exec backend alembic upgrade head
```

### 5. Seed practitioners (create sample stylists)
```bash
docker compose exec backend python scripts/seed_data.py
```

### 6. Test the application
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs
- Adminer: http://localhost:8080 (server: `postgres`, user: `salon_user`, password: `salon_password`, db: `salon_scheduler`)

---

## 🧪 Testing Stripe Webhooks Locally

1. Install Stripe CLI and login.
2. Start the listener:
   ```bash
   stripe listen --forward-to http://host.docker.internal:8000/api/v1/webhooks/stripe
   ```
3. Copy the generated `whsec_...` and set it as `STRIPE_WEBHOOK_SECRET` in `.env`.
4. Trigger a test event:
   ```bash
   stripe trigger payment_intent.succeeded
   ```

---

## 🗂️ Seed Data

- **Salons** – fetched from Google Places (cached in DB).
- **Practitioners** – generated via `scripts/seed_data.py` (8 roles per salon: Senior Stylist, Junior Stylist, Color Specialist, Blowout Specialist, Nail Technician, Makeup Artist, Waxing Specialist, Facial Specialist). Each practitioner gets random ratings, photos from `randomuser.me`, and default opening hours.

---

## 🧠 AI Stylist Matching – How It Works

The `/ai/match-stylist` endpoint returns top‑3 stylists based on a weighted score:

| Factor | Weight | Description |
|--------|--------|-------------|
| Expertise | 35% | Does the stylist offer the requested service? |
| Rating | 20% | Average customer rating (0‑5 → 0‑100%) |
| Review sentiment | 15% | Analysed with TextBlob (‑1 to 1 → 0‑100%) |
| Workload | 10% | Fewer upcoming appointments = higher score |
| Distance | 10% | Closer to customer = higher score (if coordinates provided) |
| Customer preference | 10% | Preferred stylist or past booking history |

The response includes a detailed breakdown and an explanation.

---

## 📦 Environment Variables

See `.env.example` for all variables. Critical ones:

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis URL for Celery broker & cache |
| `GOOGLE_PLACES_API_KEY` | Places API key (also used for Maps frontend) |
| `STRIPE_SECRET_KEY` | Stripe test secret key |
| `STRIPE_PUBLISHABLE_KEY` | Stripe test publishable key |
| `STRIPE_WEBHOOK_SECRET` | Webhook signing secret (from Stripe CLI) |
| `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` | Twilio credentials |
| `RESEND_API_KEY` | Resend email API key |
| `SECRET_KEY` | JWT secret (for future auth) |
| `BOOKING_MIN_ADVANCE_HOURS` | Minimum hours before booking (default 1) |
| `BOOKING_MAX_ADVANCE_DAYS` | Maximum days in advance (default 90) |

---

## 🐞 Edge Cases Handled

| Case | Solution |
|------|----------|
| Two users book same slot simultaneously | Database row‑level lock + `UniqueConstraint` (partial) + application‑level check |
| Practitioner sick day | `POST /practitioners/{id}/unavailable` – cancels & refunds affected appointments, notifies customers |
| 60‑min service (vs 30‑min slots) | Blocks two consecutive slots |
| Cancellation opens a slot | Immediately notifies waitlist (first in line) |
| Google Places API down | Serves cached data with warning header |
| Preferred stylist fully booked | AI matching suggests alternatives with explanation |
| 50 concurrent booking attempts | Connection pooling, database indexes, idempotency keys |

---

## 📝 Assumptions & Limitations

- **Authentication** – Not implemented (customers are identified by phone number). For practitioner/admin endpoints, a simple API key or JWT would be added in production.
- **Practitioner data** – Google Places does not provide individual stylist details; we seed practitioners with realistic data.
- **Opening hours** – Google Places sometimes returns no hours; we fall back to default 9 AM‑6 PM (Mon‑Fri), 10 AM‑4 PM (Sat), closed Sun.
- **Cancellation refunds** – Only deposit is refunded (final payment not yet implemented; deposit is 20% of total price).
- **Waitlist expiry** – Entries expire after 7 days.
- **Email sender** – Resend sandbox uses `onboarding@resend.dev`; custom domain not verified.

---

## 🎥 Video Walkthrough

A 10‑15 minute video explaining the project is available at:  
**`[Insert YouTube / Google Drive link]`**

The video covers:
- Demo of the full flow (search → book → pay → cancel → waitlist)
- Database design & double‑booking prevention
- AI stylist matching algorithm
- Handling of edge cases (concurrent booking, sick day, API fallback)
- Challenges faced and solutions

---

## 👥 Team & Submission

- **Hackathon:** ZySec Tech Hackathon 2026
- **Project Option:** Smart Salon Scheduler (Project Two)
- **Submitted by:** `[Your Name]`
- **Email:** `[Your Email]`

**Submission email:** `hr@zysec.ai`  
**Subject:** `ProjectTwo Submission - YourName`

---

## 📄 License

This project is for educational/hackathon purposes only. All third‑party APIs (Google, Stripe, Twilio, Resend) are used under their respective free tiers.

---

**Thank you for reviewing!**  
For any issues, please open a GitHub issue or contact the author.