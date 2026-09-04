from rest_framework import serializers
from .models import *
from apps.users.serializers import ProfileSerializer, PageSerializer


class NotificationSerializer(serializers.ModelSerializer):
    donater = ProfileSerializer(source='donater.profile',read_only=True)
    donatee = PageSerializer(read_only=True)
    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ["donater","donatee","transaction","created_at"]