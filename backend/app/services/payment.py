import stripe
from app.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentService:
    @staticmethod
    async def create_deposit_intent(appointment_id: int, amount: float, customer_email: str, customer_name: str):
        """Create a Stripe PaymentIntent for the deposit (non‑redirect methods only)."""
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # cents
            currency="usd",
            metadata={"appointment_id": appointment_id},
            receipt_email=customer_email,
            description=f"Deposit for appointment #{appointment_id}",
            automatic_payment_methods={
                "enabled": True,
                "allow_redirects": "never"
            }
        )
        return intent

    @staticmethod
    async def verify_deposit(payment_intent_id: str) -> bool:
        """Verify that the PaymentIntent succeeded."""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return intent.status == "succeeded"
        except stripe.error.StripeError:
            return False

    @staticmethod
    async def process_refund(payment_intent_id: str, amount: float) -> bool:
        """Refund a specific amount (partial or full)."""
        try:
            stripe.Refund.create(
                payment_intent=payment_intent_id,
                amount=int(amount * 100)
            )
            return True
        except stripe.error.StripeError:
            return False

    @staticmethod
    async def capture_final_payment(appointment_id: int, remaining_amount: float, payment_method_id: str):
        """Charge remaining amount after service completion."""
        intent = stripe.PaymentIntent.create(
            amount=int(remaining_amount * 100),
            currency="usd",
            payment_method=payment_method_id,
            confirm=True,
            metadata={"appointment_id": appointment_id, "type": "final_payment"},
            automatic_payment_methods={
                "enabled": True,
                "allow_redirects": "never"
            }
        )
        return intent