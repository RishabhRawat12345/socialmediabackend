from django.urls import path
from .views import PostListCreateView, PostDetailView,MyPostListView

urlpatterns = [
    path('', PostListCreateView.as_view(), name='post-list-create'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('myposts/', MyPostListView.as_view(), name='my-posts'),
]
