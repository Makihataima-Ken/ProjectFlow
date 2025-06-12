from django.shortcuts import render, redirect
from ProjectFlow import settings
from .models import Notification
from rest_framework_simplejwt.authentication import JWTAuthentication
import jwt
from rest_framework.decorators import authentication_classes
from django.contrib.auth import get_user_model

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

@authentication_classes([JWTAuthentication])
def view_notifications(request):
    user = get_authenticated_user(request=request)
    if not user:
        return redirect('login_page')
    
    notifications = user.notifications.all()
    return render(request, 'notifications/list.html', {'notifications': notifications})

@authentication_classes([JWTAuthentication])
def mark_as_read(request, notification_id):
    user = get_authenticated_user(request=request)
    if not user:
        return redirect('login_page')
    
    try:
        notification = user.notifications.get(id=notification_id)
        notification.is_read = True
        notification.save()
        return redirect(notification.task.get_absolute_url() if notification.task else 'home')
    except Notification.DoesNotExist:
        return redirect('home')

@authentication_classes([JWTAuthentication])
def mark_all_as_read(request):
    user = get_authenticated_user(request=request)
    if not user:
        return redirect('login_page')
    
    user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('view_notifications')