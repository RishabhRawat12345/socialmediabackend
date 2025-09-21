from django.urls import path
from . import views

urlpatterns = [
    # User Management
    path("users/", views.list_users, name="list_users"),
    path("users/<int:user_id>/", views.user_details, name="user_details"),
    path("users/<int:user_id>/deactivate/", views.deactivate_user, name="deactivate_user"),

    # Content Management
    path("posts/", views.list_posts, name="list_posts"),
    path("posts/<int:post_id>/", views.delete_post, name="delete_post"),

    # Statistics
    path("stats/", views.stats, name="stats"),
]
