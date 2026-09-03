from notification import serializers
from user.serializers import ProfileSerializer, PageSerializer
from .models import *

class BlockSerializer(serializers.ModelSerializer):
    blocker = PageSerializer(read_only=True)
    blockee = ProfileSerializer(source='blockee.profile',read_only=True)
    class Meta:
        model = Block
        fields='__all__'