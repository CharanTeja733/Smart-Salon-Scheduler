#!/usr/bin/env python3
"""
Manual confirmation of a Stripe PaymentIntent for testing.
Usage: python confirm_payment.py <payment_intent_id_or_client_secret>
Example: python confirm_payment.py pi_3TfhCiB9LM0uESrk1IIDzjOm
         or with client_secret: python confirm_payment.py pi_3TfhCiB9LM0uESrk1IIDzjOm_secret_...
"""

import os
import sys
import stripe

# ---------- CONFIGURATION ----------
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")

if not STRIPE_SECRET_KEY or STRIPE_SECRET_KEY == "sk_test_...":
    print("❌ Please set your Stripe secret key in the environment variable STRIPE_SECRET_KEY")
    sys.exit(1)

stripe.api_key = STRIPE_SECRET_KEY

TEST_PAYMENT_METHOD = "pm_card_visa"

def extract_payment_intent_id(input_str: str) -> str:
    """Extract the PaymentIntent ID from a full client_secret or just return the ID."""
    if "_secret_" in input_str:
        return input_str.split("_secret_")[0]
    return input_str

def confirm_payment_intent(payment_intent_id: str):
    try:
        intent = stripe.PaymentIntent.confirm(
            payment_intent_id,
            payment_method=TEST_PAYMENT_METHOD,
        )
        print(f"✅ PaymentIntent confirmed: {intent.id}")
        print(f"   Status: {intent.status}")
        print(f"   Amount: {intent.amount / 100:.2f} {intent.currency.upper()}")
        return intent
    except stripe.error.StripeError as e:
        print(f"❌ Stripe error: {e.user_message}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python confirm_payment.py <payment_intent_id_or_client_secret>")
        sys.exit(1)

    raw_input = sys.argv[1]
    payment_intent_id = extract_payment_intent_id(raw_input)
    confirm_payment_intent(payment_intent_id)