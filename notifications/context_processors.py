from django.shortcuts import redirect

def notifications(request):
    if request.user.is_authenticated:
        return {
            'unread_notifications': request.user.notifications.filter(is_read=False),
            'recent_notifications': request.user.notifications.all()[:5]
        }
    return {}