from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.view_notifications, name='view_notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_as_read, name='mark_as_read'),
    path('notifications/mark-all-read/', views.mark_all_as_read, name='mark_all_as_read'),
]