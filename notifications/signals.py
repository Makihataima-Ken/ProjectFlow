from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from tasks.models import Task
from comments.models import Comment
from notifications.models import Notification

User = get_user_model()

@receiver(post_save, sender=Task)
def task_notification(sender, instance, created, **kwargs):
    if created:
        # Notification for task assignment
        Notification.objects.create(
            recipient=instance.user,
            sender=instance.project.project_manager,
            notification_type='task_assigned',
            task=instance
        )
    else:
        # Notification for task updates
        if instance.status == 'DN':  # Task completed
            Notification.objects.create(
                recipient=instance.project.project_manager,
                sender=instance.user,
                notification_type='task_completed',
                task=instance
            )
        else:
            # General task update
            Notification.objects.create(
                recipient=instance.user,
                sender=instance.project.project_manager,
                notification_type='task_updated',
                task=instance
            )

@receiver(post_save, sender=Comment)
def comment_notification(sender, instance, created, **kwargs):
    if created:
        # Notification to task assignee (if commenter is not the assignee)
        if instance.author != instance.task.user:
            Notification.objects.create(
                recipient=instance.task.user,
                sender=instance.author,
                notification_type='comment_added',
                task=instance.task,
                comment=instance
            )
        
        # Notifications for mentioned users
        for mentioned_user in instance.mentions.all():
            Notification.objects.create(
                recipient=mentioned_user,
                sender=instance.author,
                notification_type='mentioned',
                task=instance.task,
                comment=instance
            )