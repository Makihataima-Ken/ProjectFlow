# forms.py
from django import forms
from .models import Comment
# from .models import CommentAttachment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Add a comment...'
            })
        }

# class AttachmentForm(forms.ModelForm):
#     files = forms.FileField(
#         widget=forms.ClearableFileInput(attrs={
#             'multiple': True,
#             'class': 'form-control'
#         }),
#         required=False
#     )
    
#     class Meta:
#         model = CommentAttachment
#         fields = ['description']