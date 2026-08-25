from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import ProfileSerializer, PrivateProfileSerializer, PageSerializer, PrivatePageSerializer
from .selectors import get_profile_or_400, get_user_profile, get_user_page, get_page
from .services import update_profile


class ProfileModify(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return get_user_profile(user_id=self.request.user.id)

class PrivateProfileModify(generics.RetrieveUpdateAPIView):
    serializer_class = PrivateProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return get_user_profile(user_id=self.request.user.id)
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
        update_profile(
            user_id=self.request.user.id,
            data= serializer.validated_data,
        )
class PageModify(generics.RetrieveUpdateDestroyAPIView): # dùng cái page serializer sẽ chỉ chỉnh sửa 1 số field và lấy ra 1 số field
    serializer_class = PageSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return get_user_page(user_id=self.request.user.id)
class PrivatePageModify(generics.RetrieveUpdateAPIView): #lấy ra chỉ các field private và chỉnh sửa nó
    serializer_class = PrivatePageSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return get_user_page(user_id=self.request.user.id)

class PageView(generics.RetrieveAPIView):#lấy page truyền vào
    serializer_class = PageSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        page_id = self.request.data.get('page_id')
        return get_page(page_id=page_id)
