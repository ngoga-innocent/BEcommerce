# accounts/views.py
from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserUpdateSerializer, CustomTokenObtainPairSerializer,AdminUserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PasswordResetOTP, PasswordResetToken
from functions.otpfunctions import generate_otp, hash_otp
from functions.send_mail import send_otp_email
from django.core.mail import send_mail, BadHeaderError
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password
import logging
User = get_user_model()
logger = logging.getLogger(__name__)
# ------------------- Registration -------------------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
# ------------------- Login with user info -------------------
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# ------------------- Update user -------------------
class UserUpdateView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]  # only admins allowed
class ForgotPasswordAPIView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"detail": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # 1️⃣ Get user
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Prevent email enumeration
                return Response({"error": True,"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # 2️⃣ Generate OTP
            try:
                otp = generate_otp()
            except Exception as e:
                logger.error(f"OTP generation failed for {email}: {e}")
                return Response(
                    {"detail": "Failed to generate OTP"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # 3️⃣ Save OTP to DB
            try:
                PasswordResetOTP.objects.create(
                    user=user,
                    otp_hash=hash_otp(otp),
                    expires_at=timezone.now() + timedelta(minutes=10),
                )
            except Exception as e:
                logger.error(f"Failed to save OTP for {email}: {e}")
                return Response(
                    {"detail": "Failed to save OTP"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # 4️⃣ Send email
            # try:
            #     send_mail(
            #         subject="Your Password Reset OTP",
            #         message=f"Your OTP is {otp}. It expires in 10 minutes.",
            #         from_email="My Next Market <no-reply@mynextmarket.com>",
            #         recipient_list=[email],
            #         fail_silently=False,
            #     )
            # except BadHeaderError:
            #     logger.error(f"Invalid email header when sending OTP to {email}")
            #     return Response(
            #         {"detail": "Invalid email header"},
            #         status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            #     )
            try:
                send_otp_email(email, otp)
            except Exception as e:
                print("Failed to send OTP email:", e)
                return Response(
                    {"detail": "Failed to send OTP email. Try again later."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            except Exception as e:
                logger.error(f"Failed to send OTP email to {email}: {e}")
                return Response(
                    {"detail": "Failed to send email. Please try again later."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # ✅ Success
            return Response(
                {"success": True, "message": "OTP sent to email"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            # Catch-all for any unexpected error
            logger.exception(f"Forgot password error for {email}: {e}")
            return Response(
                {"detail": "Something went wrong. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
class VerifyResetOTPAPIView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response(
                {"detail": "Email and OTP are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # 1️⃣ Get user
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {"detail": "Invalid OTP"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 2️⃣ Get OTP object
            otp_obj = PasswordResetOTP.objects.filter(
                user=user,
                otp_hash=hash_otp(otp),
                is_used=False,
            ).order_by("-created_at").first()

            if not otp_obj or otp_obj.is_expired():
                return Response(
                    {"detail": "Invalid or expired OTP"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 3️⃣ Mark OTP as used
            otp_obj.is_used = True
            otp_obj.save()

            # 4️⃣ Create reset token
            reset_token = PasswordResetToken.objects.create(
                user=user,
                expires_at=timezone.now() + timedelta(minutes=10),
            )

            return Response(
                {
                    "success": True,
                    "reset_token": str(reset_token.token),
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.exception(f"Error verifying OTP for {email}: {e}")
            return Response(
                {"detail": "Something went wrong. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ResetPasswordAPIView(APIView):
    permission_classes = []

    def post(self, request):
        token = request.data.get("reset_token")
        new_password = request.data.get("new_password")

        if not token or not new_password:
            return Response(
                {"detail": "Token and new password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # 1️⃣ Get token object
            try:
                token_obj = PasswordResetToken.objects.get(
                    token=token,
                    is_used=False,
                )
            except PasswordResetToken.DoesNotExist:
                return Response(
                    {"detail": "Invalid reset token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 2️⃣ Check if token expired
            if token_obj.is_expired():
                return Response(
                    {"detail": "Reset token expired"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 3️⃣ Update user password
            user = token_obj.user
            user.password = make_password(new_password)
            user.save()

            # 4️⃣ Mark token as used
            token_obj.is_used = True
            token_obj.save()

            return Response(
                {"success": True, "message": "Password reset successful"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.exception(f"Error resetting password for token {token}: {e}")
            return Response(
                {"detail": "Something went wrong. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )