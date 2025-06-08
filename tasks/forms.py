from django import forms
from django.contrib.auth import get_user_model
from .models import Task
from projects.models import Project
from django.db.models import Q

User = get_user_model()

class TaskForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        # Set up project field
        if self.project:
            self.fields['project'].initial = self.project
            self.fields['project'].widget = forms.HiddenInput()
        else:
            self.fields['project'].queryset = Project.objects.filter(
                Q(project_manager=user) | Q(participants=user)
            ).distinct()

        # Set up user assignment field
        if self.project:
            self.fields['user'].queryset = self.get_assignable_users()
            if not self.instance.pk:  # Only for new tasks
                self.initial['user'] = user.id  # Default to current user
        elif 'project' in self.data:
            try:
                project_id = int(self.data.get('project'))
                project = Project.objects.get(id=project_id)
                self.fields['user'].queryset = self.get_assignable_users(project)
            except (ValueError, Project.DoesNotExist):
                pass

    def get_assignable_users(self, project=None):
        project = project or self.project
        if not project:
            return User.objects.none()
        return User.objects.filter(
            Q(participating_projects=project) | 
            Q(pk=project.project_manager.pk)
        ).distinct()

    def clean(self):
        cleaned_data = super().clean()
        project = cleaned_data.get('project') or self.project
        
        # Ensure task has a user
        if not cleaned_data.get('user'):
            cleaned_data['user'] = self.user
            
        # Validate user is in project
        if project and cleaned_data['user']:
            if (cleaned_data['user'] not in project.participants.all() and
                cleaned_data['user'] != project.project_manager):
                raise forms.ValidationError(
                    "Assigned user must be a project participant or manager"
                )
        return cleaned_data

    class Meta:
        model = Task
        fields = ['project', 'user', 'title', 'description', 'due_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'user': forms.Select(attrs={'class': 'form-select select2'}),
        }


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
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
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
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    
    project = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Project.objects.none(),
        widget=forms.SelectMultiple(attrs={
            'class': 'select2-multiple form-control',
            'data-placeholder': 'Filter by project...'
        })
    )
    
    assigned_to = forms.ModelMultipleChoiceField(
        required=False,
        queryset=User.objects.none(),
        widget=forms.SelectMultiple(attrs={
            'class': 'select2-multiple form-control',
            'data-placeholder': 'Filter by assignee...'
        })
    )
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Project filtering
            self.fields['project'].queryset = Project.objects.filter(
                Q(project_manager=user) | Q(participants=user)
            ).distinct()
            
            # User filtering
            self.fields['assigned_to'].queryset = User.objects.filter(
                Q(managed_projects__participants=user) | 
                Q(participating_projects__project_manager=user)
            ).distinct()