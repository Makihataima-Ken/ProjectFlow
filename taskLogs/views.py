from django.shortcuts import render

from django.core.paginator import Paginator
from rest_framework.decorators import api_view, permission_classes

from django.shortcuts import render, get_object_or_404
import jwt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from ProjectFlow import settings
from taskLogs.models import TaskLog
from tasks.permissions import IsTaskParticipant
from .models import Task

from django.contrib.auth import get_user_model
User = get_user_model()

# ========== Helper Functions ==========

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


def can_manage_task(user, task):
    """Check if user can manage this task"""
    return (
            task.project.project_manager == user
            or task.user == user)
    
def can_view_task(user, task):
    """Check if user can manage this task"""
    return (
            task.project.project_manager == user or
        user in task.project.participants.all() or
        user.is_staff)
    
# API View (DRF)
class TaskLogAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsTaskParticipant]

    def get(self, request, task_id):
        # Get the task first to verify permissions
        task = get_object_or_404(Task, pk=task_id)
        self.check_object_permissions(request, task)
        
        # Get all logs for this task, ordered by timestamp
        logs = TaskLog.objects.filter(task=task).order_by('-timestamp')
        
        # Pagination
        page_number = request.query_params.get('page', 1)
        paginator = Paginator(logs, 10)  # 10 logs per page
        page_obj = paginator.get_page(page_number)
        
        # Serialize the data
        log_data = []
        for log in page_obj:
            log_data.append({
                'id': log.id,
                'timestamp': log.timestamp,
                'user': log.user.username if log.user else 'System',
                'actions': [log.get_actions_display().get(a, a) for a in log.actions],
                'field_changed': log.field_changed,
                'old_value': log.old_value,
                'new_value': log.new_value,
                'notes': log.notes
            })
        
        return Response({
            'task_id': task.id,
            'task_title': task.title,
            'logs': log_data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'total_logs': paginator.count
            }
        })

# HTML View
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTaskParticipant])
def task_logs_view(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    
    if not can_view_task(request.user, task):
        return render(request, 'tasks/error.html', {'error': 'Not authorized'})
    
    logs = TaskLog.objects.filter(task=task).order_by('-timestamp')
    
    # Pagination
    paginator = Paginator(logs, 10)  # 10 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'tasks/task_logs.html', {
        'task': task,
        'logs': page_obj,
        'action_choices': dict(TaskLog.ActionType.choices)
    })
