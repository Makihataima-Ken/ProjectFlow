from rest_framework import permissions
from .models import Task
from projects.models import Project

class IsTaskManagerOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow project managers or staff members to manage tasks.
    """
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        # Allow staff members to do anything
        if request.user.is_staff:
            return True
            
        # For task objects
        if isinstance(obj, Task):
            return obj.project.can_assign_tasks(request.user)
            
        # For project objects
        if isinstance(obj, Project):
            return obj.can_assign_tasks(request.user)
            
        return False

class IsTaskParticipant(permissions.BasePermission):
    """
    Custom permission to only allow users who are assigned to the task,
    project managers, or project participants to view tasks.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Allow staff members to do anything
        if request.user.is_staff:
            return True

        # Check if user is assigned to the task
        if obj.user == request.user:
            return True

        # Check if user is project manager
        if obj.project.project_manager == request.user:
            return True

        # Check if user is project participant
        if request.user in obj.project.participants.all():
            return True

        return False

class CanSearchTasks(permissions.BasePermission):
    """
    Custom permission to only allow users to search tasks they have access to.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True 