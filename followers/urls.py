from django.urls import path
from .views import FollowUserView, FollowersListView, FollowingListView, FollowStatsView

urlpatterns = [
    path('<int:user_id>/follow/', FollowUserView.as_view(), name='follow-user'),
    path('<int:user_id>/followers/', FollowersListView.as_view(), name='user-followers'),
    path('<int:user_id>/following/', FollowingListView.as_view(), name='user-following'),
    path('<int:user_id>/stats/', FollowStatsView.as_view(), name='follow-stats'),
]
