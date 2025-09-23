from django.urls import path
from .views import (
    UserListView,
    UserProfileDetailView,
    UserProfileUpdateView,
    MyProfileDetailView,   # ✅ Added this missing import
    MyProfileUpdateView,
)

urlpatterns = [
    path('', UserListView.as_view(), name='profile-list'),
    path('me/', MyProfileDetailView.as_view(), name='my-profile-detail'),
    path('me/update/', MyProfileUpdateView.as_view(), name='my-profile-update'),
    path('<int:pk>/', UserProfileDetailView.as_view(), name='profile-detail'),
    path('<int:pk>/update/', UserProfileUpdateView.as_view(), name='profile-update'),
]
