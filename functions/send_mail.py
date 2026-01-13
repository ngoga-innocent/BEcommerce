from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
# def send_otp_email(email, otp):
#     subject = "Password Reset OTP"
#     message = f"""
# Hello,

# Your password reset OTP is:

# {otp}

# This OTP will expire in 10 minutes.
# If you did not request this, ignore this email.

# My Next Market
# """

#     send_mail(
#         subject,
#         message,
#         settings.DEFAULT_FROM_EMAIL,
#         [email],
#         fail_silently=False,
#     )


def send_otp_email(to_email: str, otp: str):
    """
    Send a beautiful HTML OTP email
    """
    subject = "Your My Next Market OTP Code"
    from_email = settings.DEFAULT_FROM_EMAIL

    # Render HTML template
    html_content = render_to_string("emails/otp_email.html", {"otp": otp})
    text_content = f"Your OTP code is: {otp}\n\nUse this code to reset your password."

    email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    email.attach_alternative(html_content, "text/html")

    try:
        email.send(fail_silently=False)
        print(f"OTP sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send OTP email to {to_email}: {str(e)}")
        raise
