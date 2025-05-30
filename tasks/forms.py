from django import forms
from .models import Task
from projects.models import Project
# from accounts.models import User  # Adjust if your user model import is different

from django.db.models import Q

class TaskForm(forms.ModelForm):
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        initial = kwargs.get('initial') or {}
        self.project_instance = initial.get('project') or kwargs.pop('project', None)

        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['project'].queryset = Project.objects.filter(
                Q(project_manager=self.user) | Q(participants=self.user)
            ).distinct()

        if self.project_instance:
            self.fields['user'].queryset = self.project_instance.participants.all()
            self.fields['project'].initial = self.project_instance
            self.fields['project'].widget = forms.HiddenInput()


    class Meta:
        model = Task
        fields = ['project', 'user', 'title', 'description', 'due_date', 'status']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
