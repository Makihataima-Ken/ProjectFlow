from django.urls import path
from .views import follow_task, unfollow_task, toggle_follow_task

urlpatterns = [
    path('tasks/<int:task_id>/follow/', follow_task, name='follow_task'),
    path('tasks/<int:task_id>/unfollow/', unfollow_task, name='unfollow_task'),
    path('tasks/<int:task_id>/toggle-follow/', toggle_follow_task, name='toggle_follow_task'),
]