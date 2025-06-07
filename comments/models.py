from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from tasks.models import Task

class Comment(models.Model):
    """Model representing comments on tasks"""
    task = models.ForeignKey(
        Task,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Related Task'
    )
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Comment Author'
    )
    content = models.TextField(
        verbose_name='Comment Content',
        max_length=1000
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Created At'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )
    # Many-to-many relationship for user mentions in comments
    mentions = models.ManyToManyField(
        User,
        related_name='mentioned_in_comments',
        blank=True,
        verbose_name='Mentioned Users'
    )
    # # Many-to-many relationship for attachments
    # attachments = models.ManyToManyField(
    #     'CommentAttachment',
    #     related_name='comments',
    #     blank=True,
    #     verbose_name='Attachments'
    # )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        indexes = [
            models.Index(fields=['task', 'created_at']),
            models.Index(fields=['author']),
        ]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"

    def save(self, *args, **kwargs):
        """Override save to parse mentions in content"""
        super().save(*args, **kwargs)
        self.parse_mentions()

    def parse_mentions(self):
        """Parse @mentions in comment content and update mentions field"""
        from django.contrib.auth import get_user_model
        import re
        
        User = get_user_model()
        self.mentions.clear()
        
        # Find all @username mentions in content
        usernames = re.findall(r'@(\w+)', self.content)
        for username in usernames:
            try:
                user = User.objects.get(username=username)
                if user != self.author:  # Don't add author as a mention
                    self.mentions.add(user)
            except User.DoesNotExist:
                pass


# class CommentAttachment(models.Model):
#     """Model for file attachments to comments"""
#     file = models.FileField(
#         upload_to='comment_attachments/%Y/%m/%d/',
#         verbose_name='Attachment File'
#     )
#     uploaded_by = models.ForeignKey(
#         User,
#         related_name='comment_attachments',
#         on_delete=models.CASCADE,
#         verbose_name='Uploaded By'
#     )
#     uploaded_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name='Uploaded At'
#     )
#     description = models.CharField(
#         max_length=255,
#         blank=True,
#         verbose_name='Description'
#     )

#     class Meta:
#         verbose_name = 'Comment Attachment'
#         verbose_name_plural = 'Comment Attachments'

#     def __str__(self):
#         return f"Attachment: {self.file.name}"

#     def delete(self, *args, **kwargs):
#         """Delete the file from storage when the model is deleted"""
#         storage, path = self.file.storage, self.file.path
#         super().delete(*args, **kwargs)
#         storage.delete(path)