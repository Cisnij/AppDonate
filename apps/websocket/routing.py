from django.urls import re_path
from .NotificationConsumer import NotificationConsumer
wsPattern =[
    re_path(r'^ws/notifications/$', NotificationConsumer.as_asgi()), # $ để kết thúc cuối cùng k đc thêm gì

]