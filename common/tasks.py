from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
import logging
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import subprocess
import os
from datetime import datetime
from django.conf import settings

logger = logging.getLogger(__name__)

# shared_task: dùng được ở mọi app mà không cần import trực tiếp celery app
# bind=True: cho phép dùng self để retry
# max_retries=3: thử lại tối đa 3 lần nếu lỗi
# default_retry_delay=10: chờ 10 giây trước khi retry


