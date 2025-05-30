from django import forms
from .models import Task
from projects.models import Project

from django.contrib.auth import get_user_model
from django.db.models import Q
# from accounts.models import User  # Adjust if your user model import is different

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


User = get_user_model()

class TaskSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search tasks...',
            'class': 'form-control'
        })
    )
    
    status = forms.MultipleChoiceField(
        required=False,
        choices=Task.Status.choices,
        widget=forms.CheckboxSelectMultiple
    )
    
    due_date = forms.ChoiceField(
        required=False,
        choices=[
            ('today', 'Due Today'),
            ('week', 'Due This Week'),
            ('month', 'Due This Month'),
            ('overdue', 'Overdue'),
            ('future', 'Future'),
            ('no_date', 'No Due Date')
        ],
        widget=forms.RadioSelect
    )
    
    project = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Project.objects.none(),
        widget=forms.SelectMultiple(attrs={
            'class': 'select2-multiple',
            'data-placeholder': 'Filter by project...'
        })
    )
    
    assigned_to = forms.ModelMultipleChoiceField(
        required=False,
        queryset=User.objects.none(),
        widget=forms.SelectMultiple(attrs={
            'class': 'select2-multiple',
            'data-placeholder': 'Filter by assignee...'
        })
    )
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Only show projects the user is involved with
            self.fields['project'].queryset = Project.objects.filter(
                Q(project_manager=user) | Q(participants=user)
            ).distinct()
            
            # Only show users the user works with
            self.fields['assigned_to'].queryset = User.objects.filter(
                Q(managed_projects__participants=user) | 
                Q(participating_projects__project_manager=user)
            ).distinct()