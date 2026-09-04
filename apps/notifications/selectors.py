from django.db.models import QuerySet

from apps.notifications.models import Notification


def get_user_notifications(*,page_id:int)-> QuerySet[Notification]: # lấy tất cả thông báo của page
    notifications = Notification.objects.filter(donatee_id=page_id)
    return notifications