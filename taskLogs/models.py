from django.db import models

from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import JSONField

class TaskLog(models.Model):
    class ActionType(models.TextChoices):
        CREATE = 'CR', 'Created'
        UPDATE = 'UP', 'Updated'
        STATUS_CHANGE = 'SC', 'Status Changed'
        DELETE = 'DL', 'Deleted'
        ASSIGNEE_CHANGE = 'AC', 'Assignee Changed'
        DUE_DATE_CHANGE = 'DC', 'Due Date Changed'
        DESCRIPTION_CHANGE = 'DE', 'Description Changed'
        TITLE_CHANGE = 'TC', 'Title Changed'
    
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
    
    action = JSONField(
        models.CharField(max_length=2, choices=ActionType.choices),
        default=list,
        blank=True
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
    
        
    def get_actions_display(self):
        return {action: label for action, label in self.ActionType.choices}
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Task Log'
        verbose_name_plural = 'Task Logs'
        indexes = [
            models.Index(fields=['task']),
            models.Index(fields=['user']),
            models.Index(fields=['timestamp']),
        ]