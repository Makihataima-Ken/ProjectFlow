from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import jwt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from ProjectFlow import settings
from .models import Task
from .forms import TaskForm
from .serializers import TaskSerializer
from projects.models import Project
import requests
import json

from django.db.models import Q

from django.contrib.auth import get_user_model
User = get_user_model()

# ========== Helper Functions ==========

def get_authenticated_user(request):
    """Helper to get user from JWT token"""
    if not hasattr(request, 'session'):
        return None

    access_token = request.session.get('access_token')
    if not access_token:
        return None

    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload.get('user_id')
    except jwt.InvalidTokenError:
        return None


def can_manage_task(user, task):
    """Check if user can manage this task"""
    return (
            task.project.project_manager == user)

# ========== API VIEWS ==========

class TaskAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        user = request.user
        if pk:
            task = get_object_or_404(Task, pk=pk)
            if not can_manage_task(user, task):
                return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        
        # Get all tasks where user is assigned or is project manager
        tasks = Task.objects.filter(
            Q(user=user) | 
            Q(project__project_manager=user) |
            Q(project__participants=user)
        ).distinct()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            project = serializer.validated_data.get('project')
            if not project.can_assign_tasks(request.user):
                return Response(
                    {'error': 'Not authorized to create tasks in this project'},
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        if not can_manage_task(request.user, task):
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = TaskSerializer(task, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        if not can_manage_task(request.user, task):
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ========== HTML VIEWS ==========

def task_list(request):
    user_id = get_authenticated_user(request)
    if not user_id:
        return redirect('login_page')

    try:
        tasks = Task.objects.filter(
            Q(user_id=user_id) | 
            Q(project__project_manager_id=user_id) |
            Q(project__participants=user_id)
        ).distinct()
        
        serializer = TaskSerializer(tasks, many=True)
        return render(request, 'tasks/task_list.html', {
            'tasks': serializer.data,
            'is_staff': request.user.is_staff if hasattr(request, 'user') else False
        })

    except Exception as e:
        return render(request, 'tasks/error.html', {'error': str(e)})

def task_detail(request, pk):
    user_id = get_authenticated_user(request)
    if not user_id:
        return redirect('login_page')

    task = get_object_or_404(Task, pk=pk)
    if not can_manage_task(request.user, task):
        return render(request, 'tasks/error.html', {'error': 'Not authorized'})

    serializer = TaskSerializer(task)
    return render(request, 'tasks/task_detail.html', {
        'task': serializer.data,
        'can_edit': can_manage_task(request.user, task)
    })

def create_task(request, project_id=None):
    user_id = get_authenticated_user(request)
    if not user_id:
        return redirect('login_page')

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return redirect('login_page')

    project = None
    if project_id:
        project = get_object_or_404(Project, pk=project_id)
        if not project.can_assign_tasks(user):
            return render(request, 'tasks/error.html', {'error': 'Not authorized'})

    if request.method == 'POST':
        form = TaskForm(user=user, data=request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            if project:
                task.project = project
            task.save()
            form.save_m2m()
            return redirect('task_list')
    else:
        initial_data = {'project': project} if project else {}
        form = TaskForm(user=user, initial=initial_data)

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'project': project
    })

def update_task(request, pk):
    user_id = get_authenticated_user(request)
    if not user_id:
        return redirect('login_page')
    
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return redirect('login_page')

    task = get_object_or_404(Task, pk=pk)
    
    if not can_manage_task(user, task):
        return render(request, 'tasks/error.html', {'error': 'Not authorized'})

    if request.method == 'POST':
        form = TaskForm(user=user, data=request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(request.user, instance=task)

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'task': task
    })

def delete_task(request, pk):
    user_id = get_authenticated_user(request)
    if not user_id:
        return redirect('login_page')

    task = get_object_or_404(Task, pk=pk)
    if not can_manage_task(request.user, task):
        return render(request, 'tasks/error.html', {'error': 'Not authorized'})

    if request.method == 'POST':
        project_id = task.project.id
        task.delete()
        return redirect('project_detail', pk=project_id)

    return render(request, 'tasks/task_confirm_delete.html', {
        'task': TaskSerializer(task).data
    })

# ========== Token Refresh Helper ==========

def refresh_access_token(request):
    refresh_token = request.session.get('refresh_token')
    if not refresh_token:
        return False

    try:
        response = requests.post(
            f'{settings.BASE_URL}/api/token/refresh/',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'refresh': refresh_token})
        )
        if response.status_code == 200:
            request.session['access_token'] = response.json().get('access')
            return True
    except requests.exceptions.RequestException:
        return False
    return False