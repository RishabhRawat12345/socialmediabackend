from django.urls import path
from .views import (
    RegisterView, VerifySupabaseUserView, LoginView, LogoutView,
    PasswordResetView, PasswordResetConfirmView, ChangePasswordView,UserSearchView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify/', VerifySupabaseUserView.as_view(), name='verify-supabase-user'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  
    path('search-users/', UserSearchView.as_view(), name='search-users'),# ✅ Refresh token
]
