from django.urls import path
from .views import TaskLogAPIView, task_logs_view

urlpatterns = [
    
    # API endpoint
    path('api/tasks/<int:task_id>/logs/', TaskLogAPIView.as_view(), name='task-logs-api'),
    
    # HTML endpoint
    path('tasks/<int:task_id>/logs/', task_logs_view, name='task-logs-html'),
]