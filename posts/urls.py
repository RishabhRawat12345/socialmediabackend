from django.urls import path
from .views import (
    PostListView, PostDetailView, MyPostListView,
    LikePostView, CommentCreateView,
    NotificationListView, MarkNotificationReadView, PostCommentListView
)

urlpatterns = [
    # Posts
    path('', PostListView.as_view(), name='post-list'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('myposts/', MyPostListView.as_view(), name='my-posts'),

    # Likes
    path('<int:post_id>/like/', LikePostView.as_view(), name='post-like'),

    # Comments
    path('<int:post_id>/comments/', PostCommentListView.as_view(), name='post-comments'),
    path('<int:post_id>/comments/create/', CommentCreateView.as_view(), name='create-comment'),

    # Notifications
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:notification_id>/read/', MarkNotificationReadView.as_view(), name='mark-notification-read'),
]
