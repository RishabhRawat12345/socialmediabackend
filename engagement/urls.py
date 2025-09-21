from django.urls import path
from .views import LikePostView, LikeStatusView, CommentListCreateView, CommentDeleteView

urlpatterns = [
    path('posts/<int:post_id>/like/', LikePostView.as_view(), name='like-post'),
    path('posts/<int:post_id>/like/status/', LikeStatusView.as_view(), name='like-status'),
    path('posts/<int:post_id>/comments/', CommentListCreateView.as_view(), name='post-comments'),
    path('comments/<int:pk>/delete/', CommentDeleteView.as_view(), name='delete-comment'),
]
