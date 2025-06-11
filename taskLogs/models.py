from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class TaskLog(models.Model):
    class ActionType(models.TextChoices):
        CREATE = 'CR', 'Created'
        UPDATE = 'UP', 'Updated'
        STATUS_CHANGE = 'SC', 'Status Changed'
        DELETE = 'DL', 'Deleted'
        ASSIGNEE_CHANGE = 'AC', 'Assignee Changed'
        DUE_DATE_CHANGE = 'DC', 'Due Date Changed'
    
    task = models.ForeignKey(
        'Task',
        related_name='logs',
        on_delete=models.CASCADE
    )
    
    user = models.ForeignKey(
        User,
        related_name='task_logs',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    action = models.CharField(
        max_length=2,
        choices=ActionType.choices
    )
    
    field_changed = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    
    old_value = models.TextField(
        blank=True,
        null=True
    )
    
    new_value = models.TextField(
        blank=True,
        null=True
    )
    
    timestamp = models.DateTimeField(
        default=timezone.now
    )
    
    notes = models.TextField(
        blank=True,
        null=True
    )
    
    def __str__(self):
        return f"{self.get_action_display()} on {self.task.title} by {self.user.username if self.user else 'system'}"
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Task Log'
        verbose_name_plural = 'Task Logs'
        indexes = [
            models.Index(fields=['task']),
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['timestamp']),
        ]