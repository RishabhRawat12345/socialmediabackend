from django.urls import path
from .views import FeedListView

urlpatterns = [
    path('feed/', FeedListView.as_view(), name='feed-list'),
]
