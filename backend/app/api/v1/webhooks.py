import stripe
from fastapi import APIRouter, HTTPException, Request

from app.config import settings
from app.database import SessionLocal
from app.services.booking import BookingService

router = APIRouter()

@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload") from e
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature") from e

    # Handle event
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        appointment_id = payment_intent["metadata"].get("appointment_id")
        if appointment_id:
            db = SessionLocal()
            print("-------------------------------------------------------------------")
            await BookingService.confirm_booking(int(appointment_id), payment_intent["id"], db)
            print("-------------------------------------------------------------------")
            db.close()

    return {"status": "received"}
