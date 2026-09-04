import hashlib

from django.shortcuts import render
from django.utils import cache

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from common.documents import PageDocument
from .permissions import IsNotBlocked
from .serializers import ProfileSerializer, PrivateProfileSerializer, PageSerializer, PrivatePageSerializer, \
    WalletSerializer
from .selectors import get_profile_or_400, get_user_profile, get_user_page, get_page, get_user_wallet, get_page_for_user
from .services import update_profile, create_page, delete_page
from apps.relationships.selectors import get_blocked_ids
from apps.relationships.models import *
from elasticsearch_dsl import Q as ESQ, MultiSearch

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
    def perform_destroy(self, instance):
        delete_page(page=instance)

class PrivatePageModify(generics.RetrieveUpdateAPIView): #lấy ra chỉ các field private và chỉnh sửa nó
    serializer_class = PrivatePageSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return get_user_page(user_id=self.request.user.id)

class PageView(generics.RetrieveAPIView):#lấy page truyền vào
    serializer_class = PageSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        page_id = self.kwargs.get('page_id')
        return get_page_for_user(page_id=page_id, viewer_user=self.request.user)

class CreatePage(generics.CreateAPIView):
    serializer_class = PageSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        create_page(profile=self.request.user.profile, data=serializer.validated_data)

class GetWallet(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return get_user_wallet(user_id= self.request.user.id)

class SearchAPIView(APIView):
    permission_classes = [IsAuthenticated]  # phải đăng nhập mới search được
    throttle_scope = 'search'  # dùng scope 'search' trong settings THROTTLE_RATES

    def get(self, request):
        keyword = request.query_params.get('q', '').strip()
        try:
            page = max(int(request.query_params.get('page', 1)), 1)  # ép về int, tối thiểu 1 tránh page=0 hoặc âm
        except (ValueError, TypeError):
            page = 1  # nếu truyền ?page=abc thì fallback về trang 1 thay vì crash 500

        size = 20  # số kết quả mỗi trang
        offset = (page - 1) * size  # page=1 → offset=0 và 0->20, page=2 → offset=20 và 20->40, dùng để slice ES
        cache_key = hashlib.md5(
            f"search:{request.user.id}:{keyword}:{page}".encode()
        ).hexdigest()  # md5 để key ngắn gọn
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)  # có cache → trả về ngay, không query ES hay DB
        user = request.user
        blocked_ids =  get_blocked_ids(user_id=user.id)
        blocker_ids = [] # get_blocker_ids(user_id=user.id)
        page_search = PageDocument.search().query(
            "bool",
            should=[
                # should = OR: match 1 trong các điều kiện là được
                ESQ("bool", must=[ESQ("match_phrase", page_name=keyword)], boost=4.0),
                # match_phrase: gõ đúng cụm liền nhau → rank cao nhất
                ESQ("match", page_name={
                    "query": keyword,
                    "boost": 2.0,          # rank thấp hơn match_phrase
                    "fuzziness": "AUTO",   # tự sửa lỗi chính tả: "tran" → "trần"
                    "prefix_length": 1,    # ký tự đầu phải đúng tránh kết quả rác
                    "max_expansions": 50   # giới hạn số biến thể fuzziness sinh ra
                }),
            ],
            minimum_should_match=1  # bắt buộc match ít nhất 1 điều kiện
        )
        pages = []
        

