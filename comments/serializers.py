from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Comment

User = get_user_model()

class UserMentionSerializer(serializers.ModelSerializer):
    """Serializer for user mentions in comments"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id', 'username', 'email']

class CommentSerializer(serializers.ModelSerializer):
    
    """Serializer for Comment model"""
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    mentions = UserMentionSerializer(many=True, read_only=True)
    mentioned_users = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text="List of usernames to mention (e.g., ['user1', 'user2'])"
    )
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'task', 'author', 'content', 'created_at', 'updated_at',
            'mentions', 'mentioned_users'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'mentions']