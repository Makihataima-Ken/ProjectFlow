from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    project_manager = models.ForeignKey(
        User, 
        related_name='managed_projects',
        on_delete=models.CASCADE
    )
    
    participants = models.ManyToManyField(
        User, 
        related_name='participating_projects',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
