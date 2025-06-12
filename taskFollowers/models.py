from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from tasks.models import Task

class TaskFollower(models.Model):
    """
    Model to track users who want to follow updates on specific tasks
    """
    task = models.ForeignKey(
        Task,
        related_name='followers',
        on_delete=models.CASCADE,
        verbose_name='Followed Task'
    )
    user = models.ForeignKey(
        User,
        related_name='following_tasks',
        on_delete=models.CASCADE,
        verbose_name='Follower'
    )
    created_at = models.DateTimeField(default=timezone.now)
    receive_notifications = models.BooleanField(
        default=True,
        help_text='Whether the user should receive notifications about this task'
    )

    class Meta:
        unique_together = ('task', 'user')  # Prevent duplicate follows
        verbose_name = 'Task Follower'
        verbose_name_plural = 'Task Followers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task', 'user']),
            models.Index(fields=['user', 'receive_notifications']),
        ]

    def __str__(self):
        return f"{self.user.username} follows {self.task.title}"

    @classmethod
    def follow_task(cls, task, user, receive_notifications=True):
        """
        Helper method to follow a task
        """
        follower, created = cls.objects.get_or_create(
            task=task,
            user=user,
            defaults={'receive_notifications': receive_notifications}
        )
        if not created and follower.receive_notifications != receive_notifications:
            follower.receive_notifications = receive_notifications
            follower.save()
        return follower

    @classmethod
    def unfollow_task(cls, task, user):
        """
        Helper method to unfollow a task
        """
        cls.objects.filter(task=task, user=user).delete()