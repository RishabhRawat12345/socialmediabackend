from django.urls import path
from .views import NotificationListView, mark_notification_read, mark_all_notifications_read, create_notification

urlpatterns = [
    path('', NotificationListView.as_view(), name='notifications-list'),
    path('<int:notification_id>/read/', mark_notification_read, name='notification-read'),
    path('mark-all-read/', mark_all_notifications_read, name='notifications-mark-all-read'),
    path('create/', create_notification, name='notification-create'),
]
