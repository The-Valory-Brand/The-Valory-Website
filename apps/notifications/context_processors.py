from apps.notifications.models import Notification

def notification_context(request):
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {
            'header_notifications': unread_notifications,
            'unread_notification_count': unread_count
        }
    return {
        'header_notifications': [],
        'unread_notification_count': 0
    }
