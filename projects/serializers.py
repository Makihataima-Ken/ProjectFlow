from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Project

User = get_user_model()

class ProjectUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id', 'username', 'email']

class ProjectSerializer(serializers.ModelSerializer):
    project_manager = ProjectUserSerializer(read_only=True)
    participants = ProjectUserSerializer(many=True, read_only=True)
    
    # Write-only fields for object creation/updates
    project_manager_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='project_manager',
        write_only=True,
        required=False  # Not required if setting automatically in view
    )
    participant_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='participants',
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description',
            'project_manager', 'project_manager_id',
            'participants', 'participant_ids',
            'created', 'updated'
        ]
        read_only_fields = ['created', 'updated']

    def validate_project_manager_id(self, value):
        """Optional validation for project manager assignment"""
        request = self.context.get('request')
        if request and not request.user.is_staff:
            if value != request.user:
                raise serializers.ValidationError(
                    "You can only assign yourself as project manager unless you're staff."
                )
        return value