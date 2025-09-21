# utils/email_verification.py
from django.core.mail import send_mail
from django.urls import reverse
from .tokens import generate_email_verification_token

def send_verification_email(user, request):
    token = generate_email_verification_token(user.id)
    verification_url = request.build_absolute_uri(
        reverse("verify-email") + f"?token={token}"
    )

    send_mail(
        subject="Verify your email",
        message=f"Click this link to verify your account: {verification_url}",
        from_email="no-reply@yourapp.com",
        recipient_list=[user.email],
    )
