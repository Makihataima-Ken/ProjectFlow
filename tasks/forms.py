from django import forms
from .models import Task
from projects.models import Project

class TaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.project:
            self.fields['user'].queryset = self.project.participants.all()
            self.fields['project'].initial = self.project
            self.fields['project'].widget = forms.HiddenInput()

    class Meta:
        model = Task
        fields = ['project', 'user', 'title', 'description', 'due_date', 'status']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }