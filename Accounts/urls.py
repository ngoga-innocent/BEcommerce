# accounts/urls.py
from django.urls import path
from .views import RegisterView, AdminUserViewSet
from .views import (
    ForgotPasswordAPIView,
    VerifyResetOTPAPIView,
    ResetPasswordAPIView,
)
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r"users", AdminUserViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path("auth/forgot-password/", ForgotPasswordAPIView.as_view()),
    path("auth/verify-reset-otp/", VerifyResetOTPAPIView.as_view()),
    path("auth/reset-password/", ResetPasswordAPIView.as_view()),
    # path('users/create/', AdminUserCreateView.as_view(), name='admin_user_create'),
    # path('users/<int:pk>/', AdminUserDetailView.as_view(), name='admin_user_detail'),
    # path('api/auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]+ router.urls
