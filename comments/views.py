from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator

from .models import Comment
from tasks.models import Task
# from .models import CommentAttachment
from .forms import CommentForm
# from .forms import AttachmentForm
from .serializers import CommentSerializer


from ProjectFlow import settings
import jwt

User = get_user_model()

def get_authenticated_user(request):
    """Helper function to get user from JWT token"""
    access_token = request.session.get('access_token')
    if not access_token:
        return None
    
    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
        return User.objects.get(pk=payload.get('user_id'))
    except (jwt.InvalidTokenError, User.DoesNotExist):
        return None

class CommentAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            task = get_object_or_404(Task, pk=pk)
            comments = task.comments.all().select_related('author')
            # .prefetch_related('attachments')
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        return Response([], status=status.HTTP_200_OK)

    def post(self, request, pk):
        
        user = get_authenticated_user(request=request)
        if not user:
            return redirect('login_page')
        
        task = get_object_or_404(Task, pk=pk)
        serializer = CommentSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            comment = serializer.save(task=task, author=user)
            
            # Handle attachments
            # if 'attachments' in request.FILES:
            #     for file in request.FILES.getlist('attachments'):
            #         attachment = CommentAttachment.objects.create(
            #             file=file,
            #             uploaded_by=request.user
            #         )
            #         comment.attachments.add(attachment)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def task_comments(request, task_id):
    user = get_authenticated_user(request=request)
    if not user:
        return redirect('login_page')
    
    task = get_object_or_404(Task, pk=task_id)
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        # attachment_form = AttachmentForm(request.POST, request.FILES)
        
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.task = task
            comment.author = user
            comment.save()
            
            # if attachment_form.is_valid():
            #     for file in request.FILES.getlist('files'):
            #         attachment = CommentAttachment.objects.create(
            #             file=file,
            #             uploaded_by=request.user,
            #             description=attachment_form.cleaned_data.get('description', '')
            #         )
            #         comment.attachments.add(attachment)
            
            return redirect('task_detail', pk=task_id)
    else:
        comment_form = CommentForm()
        # attachment_form = AttachmentForm()
    
    # comments = task.comments.all().select_related('author')
    # .prefetch_related('attachments')
    
     # Get all comments and paginate them
    comments_list = task.comments.all().order_by('-created_at')
    paginator = Paginator(comments_list, 10)  # Show 10 comments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'tasks/comments.html', {
        'task': task,
        'comments': page_obj,
        'comment_form': comment_form,
        'user':user,
        # 'attachment_form': attachment_form
    })
    
def update_comment(request, comment_id):
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    comment = get_object_or_404(Comment, pk=comment_id)
    
    if comment.author != user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            updated_comment = form.save(commit=False)
            updated_comment.updated_at = timezone.now()
            updated_comment.save()
            # updated_comment.parse_mentions()
            
            # if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            #     comments = Comment.objects.filter(task=comment.task).order_by('-created_at')
            #     return JsonResponse({
            #         'comments_html': render_to_string('comments/comment_list.html', {
            #             'comments': comments,
            #             'task': comment.task,
            #             'user': request.user
            #         }, request=request)
            #     })
            return redirect('task_comments', task_id=comment.task.id)
        
        return JsonResponse({'errors': form.errors}, status=400)
    
    # # GET request - return edit form
    # if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    #     return JsonResponse({
    #         'form_html': render_to_string('comments/edit_form.html', {
    #             'comment': comment
    #         }, request=request)
    #     })
    
    return render(request, 'comments/edit_form.html', {'comment': comment})

class CommentView(View):
    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        comments = task.comments.all().select_related('author')
        # .prefetch_related('attachments')
        return render(request, 'tasks/partials/comment_list.html', {
            'comments': comments
        })

    def post(self, request, pk):
        
        user = get_authenticated_user(request=request)
        if not user:
            return redirect('login_page')
        
        task = get_object_or_404(Task, pk=pk)
        form = CommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = user
            comment.save()
            
            # Handle mentions
            comment.parse_mentions()
            
            return JsonResponse({
                'success': True,
                'comment_id': comment.id
            })
        
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)


def delete_comment(request, comment_id):
    user = get_authenticated_user(request=request)
    if not user:
        return redirect('login_page')
    
    comment = get_object_or_404(Comment, pk=comment_id, author=user)
    task_id = comment.task.id
    comment.delete()
    return redirect('task_detail', pk=task_id)

# @login_required
# def delete_attachment(request, attachment_id):
#     attachment = get_object_or_404(CommentAttachment, pk=attachment_id, uploaded_by=request.user)
#     attachment.delete()
#     return JsonResponse({'success': True})