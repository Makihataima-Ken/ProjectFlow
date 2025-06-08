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
from .forms import TaskForm, TaskSearchForm
from .serializers import TaskSerializer
from .permissions import IsTaskManagerOrStaff, IsTaskParticipant, CanSearchTasks
from projects.models import Project
import requests
import json

from django.db.models import Q

from datetime import date, timedelta
from django.utils import timezone

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

# ========== API VIEWS ==========

class TaskAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsTaskManagerOrStaff]

    def get(self, request, pk=None):
        user = get_authenticated_user(request)
        
        if pk:
            task = get_object_or_404(Task, pk=pk)
            self.check_object_permissions(request, task)
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
            user= get_authenticated_user(request)
            self.check_object_permissions(request, project)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        self.check_object_permissions(request, task)
        serializer = TaskSerializer(task, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        self.check_object_permissions(request, task)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TaskSearchAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, CanSearchTasks]

    def get(self, request):
        user = get_authenticated_user(request)
        tasks = Task.objects.filter(
            Q(user=user) | 
            Q(project__project_manager=user) |
            Q(project__participants=user)
        ).distinct()

        # Get query parameters
        query = request.query_params.get('query')
        statuses = request.query_params.getlist('status')
        due_date_filter = request.query_params.get('due_date')
        projects = request.query_params.getlist('project')
        assigned_to = request.query_params.getlist('assigned_to')
        
        if query:
            tasks = tasks.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
        
        if statuses:
            tasks = tasks.filter(status__in=statuses)
            
        if due_date_filter:
            today = timezone.now().date()
            if due_date_filter == 'today':
                tasks = tasks.filter(due_date=today)
            elif due_date_filter == 'week':
                end_week = today + timedelta(days=(6 - today.weekday()))
                tasks = tasks.filter(due_date__range=[today, end_week])
            elif due_date_filter == 'month':
                end_month = today.replace(day=28) + timedelta(days=4)
                end_month = end_month - timedelta(days=end_month.day-1)
                tasks = tasks.filter(due_date__range=[today, end_month])
            elif due_date_filter == 'overdue':
                tasks = tasks.filter(due_date__lt=today)
            elif due_date_filter == 'future':
                tasks = tasks.filter(due_date__gt=today)
            elif due_date_filter == 'no_date':
                tasks = tasks.filter(due_date__isnull=True)
        
        if projects:
            tasks = tasks.filter(project__in=projects)
            
        if assigned_to:
            tasks = tasks.filter(user__in=assigned_to)
    
        # Order by due date (nulls last) and status
        tasks = tasks.order_by('due_date', 'status')
        
        serializer = TaskSerializer(tasks, many=True)
        return Response({
            'tasks': serializer.data,
            'total_count': tasks.count(),
            'filters_applied': {
                'query': query,
                'statuses': statuses,
                'due_date_filter': due_date_filter,
                'projects': projects,
                'assigned_to': assigned_to
            }
        })

# ========== HTML VIEWS ==========

def task_list(request):
    user = get_authenticated_user(request)
    if not user:
        return redirect('login_page')

    try:
        tasks = Task.objects.filter(
            Q(project__project_manager=user) |
            Q(project__participants=user.id)
        ).distinct()
        
        serializer = TaskSerializer(tasks, many=True)
        return render(request, 'tasks/task_list.html', {
            'tasks': serializer.data,
            'is_staff': request.user.is_staff if hasattr(request, 'user') else False
        })

    except Exception as e:
        return render(request, 'tasks/error.html', {'error': str(e)})

def task_detail(request, pk):
    user= get_authenticated_user(request)
    
    if not user:
        return redirect('login_page')

    task = get_object_or_404(Task, pk=pk)
    if not can_view_task(user, task):
        return render(request, 'tasks/error.html', {'error': 'Not authorized'})

    serializer = TaskSerializer(task)
    print(serializer.data)
    return render(request, 'tasks/task_detail.html', {
        'task': serializer.data,
        'can_edit': can_manage_task(user, task)
    })

def create_task(request, project_id=None):
    user= get_authenticated_user(request)
    if not user:
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
    user= get_authenticated_user(request)
    if not user:
        return redirect('login_page')

    task = get_object_or_404(Task, pk=pk)
    
    if not task.can_user_manage(user):
        return render(request, 'tasks/error.html', {'error': 'Not authorized'})

    if request.method == 'POST':
        form = TaskForm(user=user, data=request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(user=user, instance=task)

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'task': task
    })

def delete_task(request, pk):
    user= get_authenticated_user(request)
    if not user:
        return redirect('login_page')
    
    task = get_object_or_404(Task, pk=pk)
    if not can_manage_task(user, task):
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


def task_search(request):
    user= get_authenticated_user(request)
    if not user:
        return redirect('login_page')
    
    form = TaskSearchForm(request.GET or None, user=user)
    
    tasks = Task.objects.filter(
        Q(user=user) | 
        Q(project__project_manager=user) |
        Q(project__participants=user)
    ).distinct()
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        statuses = form.cleaned_data.get('status')
        due_date_filter = form.cleaned_data.get('due_date')
        projects = form.cleaned_data.get('project')
        assigned_to = form.cleaned_data.get('assigned_to')
        
        if query:
            tasks = tasks.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
        
        if statuses:
            tasks = tasks.filter(status__in=statuses)
            
        if due_date_filter:
            today = timezone.now().date()
            if due_date_filter == 'today':
                tasks = tasks.filter(due_date=today)
            elif due_date_filter == 'week':
                end_week = today + timedelta(days=(6 - today.weekday()))
                tasks = tasks.filter(due_date__range=[today, end_week])
            elif due_date_filter == 'month':
                end_month = today.replace(day=28) + timedelta(days=4)
                end_month = end_month - timedelta(days=end_month.day-1)
                tasks = tasks.filter(due_date__range=[today, end_month])
            elif due_date_filter == 'overdue':
                tasks = tasks.filter(due_date__lt=today)
            elif due_date_filter == 'future':
                tasks = tasks.filter(due_date__gt=today)
            elif due_date_filter == 'no_date':
                tasks = tasks.filter(due_date__isnull=True)
        
        if projects:
            tasks = tasks.filter(project__in=projects)
            
        if assigned_to:
            tasks = tasks.filter(user__in=assigned_to)
    
    # Order by due date (nulls last) and status
    tasks = tasks.order_by(
        'due_date',
        'status'
    )
    
    return render(request, 'tasks/task_search.html', {
        'form': form,
        'tasks': tasks,
        'search_performed': any(field in request.GET for field in form.fields)
    })