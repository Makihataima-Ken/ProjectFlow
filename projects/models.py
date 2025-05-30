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

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created']  
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        indexes = [
            models.Index(fields=['project_manager'])
        ]
        
    def is_manager(self, user):
        return self.project_manager == user
    
    def can_assign_tasks(self, user):
        return self.is_manager(user) or user.is_staff
