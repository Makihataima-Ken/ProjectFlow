from django.shortcuts import render, redirect, get_object_or_404

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status

from .models import Project
from .serializers import ProjectSerializer


class ProjectView(APIView):
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

