from django.urls import path, include

urlpatterns = [
    path('api/auth/', include('users.urls')),
    path('api/users/', include('profiles.urls')),
    path('api/posts/', include('posts.urls')),
    path('api/users/', include('followers.urls')),
    path('api/', include('engagement.urls')),
    path('api/', include('feed.urls')),
    path('api/', include('notifications.urls')),  # <-- Add this line
    path('api/admin/', include('admin_api.urls')),

]
