from django.urls import path
from .views import (
    RegisterView, VerifySupabaseUserView, LoginView, LogoutView,
    PasswordResetView, PasswordResetConfirmView, ChangePasswordView,
    UserSearchView, TokenRefreshView,
    AdminUsersListView, AdminUserUpdateView,
    AdminPostsListView, AdminPostUpdateView
)

urlpatterns = [
    # Auth flow
    path('register/', RegisterView.as_view(), name='register'),
    path('verify/', VerifySupabaseUserView.as_view(), name='verify-supabase-user'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # JWT
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Password management
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),

    # User features
    path('search-users/', UserSearchView.as_view(), name='search-users'),

    # Admin Features
    path('admin/users/', AdminUsersListView.as_view(), name='admin-users-list'),
    path('admin/users/<int:user_id>/update/', AdminUserUpdateView.as_view(), name='admin-user-update'),
    path('admin/users/<int:user_id>/detail/', AdminUserDetailView.as_view(), name='admin-user-detail'),

    path('admin/posts/', AdminPostsListView.as_view(), name='admin-posts-list'),
    path('admin/posts/<int:post_id>/update/', AdminPostUpdateView.as_view(), name='admin-post-update'),

]
