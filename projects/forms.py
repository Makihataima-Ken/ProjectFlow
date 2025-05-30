from django import forms
from django.contrib.auth import get_user_model
from .models import Project

User = get_user_model()

class ProjectForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        # Only show users that the current user can assign
        if user.is_staff:
            self.fields['participants'].queryset = User.objects.all()
        else:
            self.fields['participants'].queryset = User.objects.exclude(pk=user.pk)
        
        # Remove project manager field for non-staff
        if not user.is_staff and 'project_manager' in self.fields:
            del self.fields['project_manager']

    class Meta:
        model = Project
        fields = ['name', 'description', 'participants']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'participants': forms.SelectMultiple(attrs={
                'class': 'select2',
                'data-placeholder': 'Select participants...'
            })
        }
        labels = {
            'name': 'Project Name',
            'description': 'Description',
            'participants': 'Team Members'
        }