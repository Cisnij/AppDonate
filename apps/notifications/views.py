from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from common.pagination import LargePagePagination
from .models import Notification
from .selectors import get_user_notifications
from .serializers import NotificationSerializer
from apps.users.selectors import get_user_or_400

class NotificationListView(generics.ListAPIView): #lấy tất cả thông báo
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    pagination_class = LargePagePagination
    def get_queryset(self):
        page_id = self.request.user.profile.page.id
        return get_user_notifications(page_id=page_id)
