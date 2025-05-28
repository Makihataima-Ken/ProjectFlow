from django.shortcuts import render, redirect, get_object_or_404

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status

from .models import Project
from .serializers import ProjectSerializer

from ProjectFlow import settings
import jwt

# ========== API VIEWS ==========

class ProjectAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            project = get_object_or_404(Project, pk=pk, project_manager=request.project_manager)
            serializer = ProjectSerializer(project)
            return Response(serializer.data)
        projects = Project.objects.filter(project_manager=request.project_manager)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(project_manager=request.project_manager)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        project = get_object_or_404(Project, pk=pk, project_manager=request.project_manager)
        serializer = ProjectSerializer(project, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        project = get_object_or_404(Project, pk=pk, project_manager=request.project_manager)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ========== HTML VIEWS ==========

def project_list(request):
    access_token = request.session.get('access_token')
    if not access_token:
        return redirect('login_page')

    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get('user_id')  

        if not user_id:
            return redirect('login_page')

        projects = Project.objects.filter(project_manager_id=user_id)
        print(projects)
        serializer = ProjectSerializer(projects, many=True)
        projects_data = serializer.data

        return render(request, 'projects/project_list.html', {'projects': projects_data})

    except jwt.InvalidTokenError:
        return render(request, 'projects/error.html', {'error': 'Invalid or expired token. Please log in again.'})



# def project_detail(request, pk):
#     access_token = request.session.get('access_token')
#     if not access_token:
#         return redirect('login_page')

#     try:
#         payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
#         user_id = payload.get('user_id')

#         if not user_id:
#             return redirect('login_page')

#         task = Task.objects.get(pk=pk,user_id=user_id)
#         serializer = TaskSerializer(task)
#         task_data = serializer.data

#         return render(request, 'tasks/task_detail.html', {'task': task_data})

#     except jwt.InvalidTokenError:
#         return render(request, 'tasks/error.html', {'error': 'Invalid or expired token. Please log in again.'})
#     except Exception as e:
#         return render(request, 'tasks/error.html', {'error': f'An error occurred: {str(e)}'})

# def create_task(request):
#     access_token = request.session.get('access_token')
#     if not access_token:
#         return redirect('login_page')

#     try:
#         payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
#         user_id = payload.get('user_id')

#         if not user_id:
#             return redirect('login_page')

#         if request.method == 'POST':
#             form = TaskForm(request.POST)
#             if form.is_valid():
#                 # Create task with the authenticated user
#                 task = form.save(commit=False)
#                 task.user_id = user_id
#                 task.save()
#                 return redirect('task_list')
#         else:
#             form = TaskForm()

#         return render(request, 'tasks/task_form.html', {'form': form})

#     except jwt.InvalidTokenError:
#         return render(request, 'tasks/error.html', {'error': 'Invalid or expired token. Please log in again.'})
#     except Exception as e:
#         return render(request, 'tasks/error.html', {'error': f'An error occurred: {str(e)}'})

# def update_task(request, pk):
#     access_token = request.session.get('access_token')
#     if not access_token:
#         return redirect('login_page')

#     try:
#         payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
#         user_id = payload.get('user_id')

#         if not user_id:
#             return redirect('login_page')

#         task = get_object_or_404(Task, pk=pk, user_id=user_id)

#         if request.method == 'POST':
#             form = TaskForm(request.POST, instance=task)
#             if form.is_valid():
#                 updated_task = form.save()        
#                 return redirect('task_list')
#         else:
#             form = TaskForm(instance=task)
#             # Serialize initial task data if needed for the template
#             serializer = TaskSerializer(task)
#             task_data = serializer.data

#         return render(request, 'tasks/task_form.html', {
#             'form': form,
#             'task': task_data
#         })

#     except jwt.InvalidTokenError:
#         return render(request, 'tasks/error.html', {'error': 'Invalid or expired token. Please log in again.'})
#     except Exception as e:
#         return render(request, 'tasks/error.html', {'error': f'An error occurred: {str(e)}'})

# def delete_task(request, pk):
#     access_token = request.session.get('access_token')
#     if not access_token:
#         return redirect('login_page')

#     try:
#         payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
#         user_id = payload.get('user_id')

#         if not user_id:
#             return redirect('login_page')

#         task = get_object_or_404(Task, pk=pk, user_id=user_id)

#         if request.method == 'POST':
#             task.delete()
#             return redirect('task_list')

#         serializer = TaskSerializer(task)
#         task_data = serializer.data

#         return render(request, 'tasks/task_confirm_delete.html', {
#             'task': task_data
#         })

#     except jwt.InvalidTokenError:
#         return render(request, 'tasks/error.html', {'error': 'Invalid or expired token. Please log in again.'})
#     except Exception as e:
#         return render(request, 'tasks/error.html', {'error': f'An error occurred: {str(e)}'})
