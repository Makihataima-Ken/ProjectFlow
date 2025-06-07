# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('tasks/<int:task_id>/comments/', views.task_comments, name='task_comments'),
    path('api/tasks/<int:task_id>/comments/', views.CommentAPIView.as_view(), name='api_task_comments'),
    # path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    # path('attachments/<int:attachment_id>/delete/', views.delete_attachment, name='delete_attachment'),
]