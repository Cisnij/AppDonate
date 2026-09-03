from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.pagination import LargePagePagination
from relationship.serializers import BlockSerializer
from .selectors import get_block, is_blocked
from .services import create_block, remove_block


# Create your views here.
class ListBLockeePage(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargePagePagination
    serializer_class = BlockSerializer
    def get_queryset(self):
        page_id = self.request.user.profile.page.id
        return get_block(page_id = page_id)

class AddBlockView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        page_id = request.user.profile.page_id

        block = create_block(
            user_id=user_id,
            page_id=page_id,
        )

        return Response(
            BlockSerializer(block).data,
            status=status.HTTP_201_CREATED,
        )
class RemoveBlockView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, user_id):
        page_id = request.user.profile.page_id

        remove_block(
            user_id=user_id,
            page_id=page_id,
        )

        return Response(
            {
                "detail": "User unblocked successfully."
            },
            status=status.HTTP_200_OK,
        )