from rest_framework import serializers
from .models import Task
from django.contrib.auth import get_user_model
from projects.models import Project

User = get_user_model()

class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ProjectSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name']  # Add other relevant fields

class TaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user = UserSummarySerializer(read_only=True)
    project = ProjectSummarySerializer()

    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'user',
            'project',
            'title',
            'description',
            'status',
            'status_display',
            'due_date',
            'created',
            'updated',
            'is_overdue'
        ]
        read_only_fields = ['user', 'created', 'updated', 'is_overdue']

    
    def validate_status(self, value):
        """Validate status field against enum choices"""
        if value not in [choice[0] for choice in Task.Status.choices]:
            raise serializers.ValidationError("Invalid status value")
        return value
    
