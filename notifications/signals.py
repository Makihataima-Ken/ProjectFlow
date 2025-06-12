from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from tasks.models import Task
from taskFollowers.models import TaskFollower
from comments.models import Comment
from notifications.models import Notification

User = get_user_model()

@receiver(post_save, sender=Task)
def task_notification(sender, instance, created, **kwargs):
    # Get all recipients who should be notified
    recipients = set()
    
    # Always include the task assignee
    recipients.add(instance.user)
    
    # Always include the project manager
    recipients.add(instance.project.project_manager)
    
    # Include all followers who want notifications
    followers = instance.followers.filter(receive_notifications=True).select_related('user')
    for follower in followers:
        recipients.add(follower.user)
    
    # Remove the sender if they're in recipients (no self-notifications)
    if hasattr(instance, 'updated_by') and instance.updated_by:
        recipients.discard(instance.updated_by)
    
    # For task creation
    if created:
        for recipient in recipients:
            Notification.objects.create(
                recipient=recipient,
                sender=instance.project.project_manager,
                notification_type='task_assigned',
                task=instance
            )
    else:
        # Get update_fields safely, defaulting to empty list if None
        update_fields = kwargs.get('update_fields') or []
        
        # For status changes or forced notifications
        if 'status' in update_fields or kwargs.get('force_notify', False):
            if instance.status == 'DN':  # Task completed
                for recipient in recipients:
                    Notification.objects.create(
                        recipient=recipient,
                        sender=instance.user,
                        notification_type='task_completed',
                        task=instance
                    )
            else:  # Other status updates
                for recipient in recipients:
                    Notification.objects.create(
                        recipient=recipient,
                        sender=instance.project.project_manager,
                        notification_type='task_updated',
                        task=instance
                    )

@receiver(post_save, sender=Comment)
def comment_notification(sender, instance, created, **kwargs):
    if created:
        # Get all recipients who should be notified
        recipients = set()
        
        # Include task assignee if commenter is not the assignee
        if instance.author != instance.task.user:
            recipients.add(instance.task.user)
        
        # Include project manager
        recipients.add(instance.task.project.project_manager)
        
        # Include all task followers who want notifications
        followers = instance.task.followers.filter(receive_notifications=True).select_related('user')
        for follower in followers:
            recipients.add(follower.user)
        
        # Remove comment author from recipients (no self-notifications)
        recipients.discard(instance.author)
        
        # Create comment notifications
        for recipient in recipients:
            Notification.objects.create(
                recipient=recipient,
                sender=instance.author,
                notification_type='comment_added',
                task=instance.task,
                comment=instance
            )
        
        # Notifications for mentioned users (these go to anyone mentioned, even if not normally subscribed)
        for mentioned_user in instance.mentions.all():
            if mentioned_user != instance.author:  # No self-mention notifications
                Notification.objects.create(
                    recipient=mentioned_user,
                    sender=instance.author,
                    notification_type='mentioned',
                    task=instance.task,
                    comment=instance
                )