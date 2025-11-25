# accounts/urls.py
from django.urls import path
from .views import RegisterView, AdminUserListView, AdminUserDetailView



urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('users/', AdminUserListView.as_view(), name='admin_user_list'),
    path('users/<int:pk>/', AdminUserDetailView.as_view(), name='admin_user_detail'),
    # path('api/auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
