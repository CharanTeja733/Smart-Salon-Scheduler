from twilio.rest import Client
import resend
from app.config import settings

twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
resend.api_key = settings.RESEND_API_KEY

class NotificationService:
    @staticmethod
    async def send_sms(to: str, message: str):
        """Send SMS using Twilio."""
        try:
            twilio_client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to
            )
            return True
        except Exception as e:
            print(f"SMS failed: {e}")
            return False

    @staticmethod
    async def send_email(to: str, subject: str, html_body: str):
        """Send email using Resend."""
        try:
            resend.Emails.send({
                "from": "noreply@salonscheduler.com",
                "to": to,
                "subject": subject,
                "html": html_body
            })
            return True
        except Exception as e:
            print(f"Email failed: {e}")
            return False

    @staticmethod
    async def send_booking_confirmation(customer_email: str, customer_name: str, appointment_details: dict):
        subject = "Booking Confirmation"
        body = f"""
        <h1>Thank you, {customer_name}!</h1>
        <p>Your appointment is confirmed:</p>
        <ul>
            <li>Stylist: {appointment_details['practitioner_name']}</li>
            <li>Date: {appointment_details['start_time']}</li>
            <li>Service: {appointment_details['service_type']}</li>
        </ul>
        <p>We look forward to seeing you!</p>
        """
        await NotificationService.send_email(customer_email, subject, body)

    @staticmethod
    async def send_reminder(customer_phone: str, customer_name: str, appointment_details: dict):
        message = f"Reminder: {customer_name}, your appointment with {appointment_details['practitioner_name']} is tomorrow at {appointment_details['start_time'].strftime('%I:%M %p')}. Reply CANCEL to cancel."
        await NotificationService.send_sms(customer_phone, message)