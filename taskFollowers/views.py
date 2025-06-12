from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Task, TaskFollower

from django.contrib.auth import get_user_model
from ProjectFlow import settings
import jwt

User = get_user_model()

def get_authenticated_user(request):
    """Helper function to get user from JWT token"""
    access_token = request.session.get('access_token')
    if not access_token:
        return None
    
    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
        return User.objects.get(pk=payload.get('user_id'))
    except (jwt.InvalidTokenError, User.DoesNotExist):
        return None

def can_view_task(user, task):
    """Check if user can manage this task"""
    return (
            task.project.project_manager == user or
        user in task.project.participants.all() or
        user.is_staff)

@require_POST
def follow_task(request, task_id):
    user = get_authenticated_user(request)
    if not user:
        return redirect('login_page')
    
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user has permission to follow (must be project participant)
    if not can_view_task(task=task,user=user):
        return JsonResponse({'status': 'error', 'message': 'You must be a project participant to follow tasks'}, status=403)
    
    # Follow the task
    TaskFollower.follow_task(task=task, user=user)
    
    # if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    #     return JsonResponse({
    #         'status': 'success',
    #         'action': 'followed',
    #         'followers_count': task.followers.count()
    #     })
    return redirect(task.get_absolute_url())

@require_POST
def unfollow_task(request, task_id):
    user = get_authenticated_user(request)
    if not user:
        return redirect('login_page')
    
    task = get_object_or_404(Task, id=task_id)
    TaskFollower.unfollow_task(task=task, user=user)
    
    # if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    #     return JsonResponse({
    #         'status': 'success',
    #         'action': 'unfollowed',
    #         'followers_count': task.followers.count()
    #     })
    return redirect(task.get_absolute_url())

def toggle_follow_task(request, task_id):
    user = get_authenticated_user(request)
    if not user:
        return redirect('login_page')
    
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user has permission to follow (must be project participant)
    if not can_view_task(task=task,user=user):
        return JsonResponse({'status': 'error', 'message': 'You must be a project participant to follow tasks'}, status=403)
    
    is_following = TaskFollower.objects.filter(task=task, user=user).exists()
    
    if is_following:
        TaskFollower.unfollow_task(task=task, user=user)
        action = 'unfollowed'
    else:
        TaskFollower.follow_task(task=task, user=user)
        action = 'followed'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'action': action,
            'followers_count': task.followers.count(),
            'is_following': not is_following
        })
    return redirect(task.get_absolute_url())