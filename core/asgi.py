"""
ASGI config for AppDonate project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.prod')

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from apps.websocket.routing import wsPattern

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Xử lý các yêu cầu HTTP thông thường
    "websocket": AllowedHostsOriginValidator(  # Bảo vệ các kết nối WebSocket từ các nguồn không được phép
        AuthMiddlewareStack(  # Xử lý xác thực người dùng cho WebSocket
            URLRouter(
                wsPattern  # Đây là danh sách các đường dẫn WebSocket đã định nghĩa trong routing.py
            )
        )
    ),

})