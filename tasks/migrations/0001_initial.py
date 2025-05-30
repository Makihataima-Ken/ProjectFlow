# Generated by Django 5.1.6 on 2025-05-14 16:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('dueDate', models.DateField(blank=True)),
                ('status', models.CharField(choices=[('TD', 'To Do'), ('IP', 'In Progress'), ('DN', 'Done')], default='TD', max_length=2)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Task',
                'verbose_name_plural': 'Tasks',
                'ordering': ['status', '-created'],
                'indexes': [models.Index(fields=['status'], name='tasks_task_status_4a0a95_idx'), models.Index(fields=['user', 'status'], name='tasks_task_user_id_c0fce1_idx')],
            },
        ),
    ]
