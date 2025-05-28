from rest_framework import serializers
from .models import Project

class ProjectSerializer(serializers.ModelSerializer):
    project_manager = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'project_manager', 'name', 'description','participants', 'created', 'updated']
        read_only_fields = ['project_manager', 'created', 'updated']