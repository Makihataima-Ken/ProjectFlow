from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status

from projects.forms import ProjectForm
from .models import Project
from .serializers import ProjectSerializer

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

# ========== API VIEWS ==========

class ProjectAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        user = request.user
        if pk:
            project = get_object_or_404(
                Project.objects.filter(
                    Q(project_manager=user) | 
                    Q(participants=user)
                ).distinct(),
                pk=pk
            )
            serializer = ProjectSerializer(project, context={'request': request})
            return Response(serializer.data)
        
        projects = Project.objects.filter(
            Q(project_manager=user) | 
            Q(participants=user)
        ).distinct()
        serializer = ProjectSerializer(projects, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            if 'project_manager' not in serializer.validated_data:
                serializer.save(project_manager=request.user)
            else:
                if not request.user.is_staff:
                    return Response(
                        {'error': 'Only staff can assign other project managers'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        project = get_object_or_404(
            Project.objects.filter(project_manager=request.user),
            pk=pk
        )
        serializer = ProjectSerializer(
            project,
            data=request.data,
            context={'request': request},
            partial=True
        )
        if serializer.is_valid():
            if 'project_manager' in serializer.validated_data and not request.user.is_staff:
                return Response(
                    {'error': 'Only staff can change project manager'},
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        project = get_object_or_404(
            Project.objects.filter(project_manager=request.user),
            pk=pk
        )
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ========== HTML VIEWS ==========

def project_list(request):
    user = get_authenticated_user(request)
    if not user:
        return redirect('login_page')

    projects = Project.objects.filter(
        Q(project_manager=user) | 
        Q(participants=user)
    ).distinct()
    
    serializer = ProjectSerializer(projects, many=True, context={'request': request})
    return render(request, 'projects/project_list.html', {
        'projects': serializer.data,
        'is_staff': user.is_staff
    })

def project_detail(request, pk):
    user = get_authenticated_user(request)
    if not user:
        return redirect('login_page')

    project = get_object_or_404(
        Project.objects.filter(
            Q(project_manager=user) | 
            Q(participants=user)
        ),
        pk=pk
    )
    serializer = ProjectSerializer(project, context={'request': request})
    return render(request, 'projects/project_detail.html', {
        'project': serializer.data,
        'can_edit': project.project_manager == user or user.is_staff
    })

def create_project(request):
    user = get_authenticated_user(request)
    if not user:
        return redirect('login_page')

    if request.method == 'POST':
        form = ProjectForm(user, request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.project_manager = user
            project.save()
            form.save_m2m()  # Save participants
            return redirect('project_list')
    else:
        form = ProjectForm(user)

    return render(request, 'projects/project_form.html', {
        'form': form,
        'action': 'Create'
    })

def update_project(request, pk):
    user = get_authenticated_user(request)
    if not user:
        return redirect('login_page')

    project = get_object_or_404(
        Project.objects.filter(project_manager=user),
        pk=pk
    )

    if request.method == 'POST':
        form = ProjectForm(user, request.POST, instance=project)
        if form.is_valid():
            form.save()
            form.save_m2m()  # Save participants
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(user, instance=project)

    return render(request, 'projects/project_form.html', {
        'form': form,
        'action': 'Update',
        'project_id': project.pk
    })

def delete_project(request, pk):
    user = get_authenticated_user(request)
    if not user:
        return redirect('login_page')

    project = get_object_or_404(
        Project.objects.filter(project_manager=user),
        pk=pk
    )

    if request.method == 'POST':
        project.delete()
        return redirect('project_list')

    return render(request, 'projects/project_confirm_delete.html', {
        'project': ProjectSerializer(project, context={'request': request}).data
    })