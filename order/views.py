from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError as DjangoValidationError

from common.pagination import LargePagePagination
from order.selectors import get_user_transaction, get_order_pending
from order.serializers import TransactionSerializer, OrderSerializer, CreateOrderSerializer, WebhookSerializer, WithdrawRequestSerializer, WithdrawSerializer
from order.services import create_order, create_withdrawrq, generate_vietqr_url, process_bank_webhook
from order.models import WithdrawRequest
from user.permissions import IsNotBlocked


# Create your views here.

class UserDonateHistory(generics.ListAPIView): #lịch sử donate của user
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    pagination_class = LargePagePagination

    def get_queryset(self):
        user_id = self.request.user.id
        return get_user_transaction(user_id=user_id)


class DonateForPage(generics.CreateAPIView): #dontate, tạo order và tạo qr dựa trên order và bank cuả mình
    permission_classes = [IsAuthenticated, IsNotBlocked]
    serializer_class = CreateOrderSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        page_id = self.kwargs.get('page_id') or serializer.validated_data.get('page_id')
        user_id = request.user.id
        amount = serializer.validated_data["amount"]
        content = serializer.validated_data.get("content", "")
        
        self.check_object_permissions(request, page_id)
        
        try:
            order = create_order(page_id=page_id, user_id=user_id, amount=amount, content=content)
            qr_url = generate_vietqr_url(order)
            
            return Response({
                'order_id': order.order_id,
                'amount': order.amount,
                'qr_url': qr_url,
                'message': 'Order created successfully. Please scan QR to pay.'
            }, status=status.HTTP_201_CREATED)
        except DjangoValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class BankWebhookAPIView(APIView): # endpoint xử lý webhook
    permission_classes = []
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = WebhookSerializer(data=request.data) # validate data mà webhook nhận từ bạnk
        if serializer.is_valid():
            try:
                process_bank_webhook(serializer.validated_data) # xử lý update order, tạo transaction, update wallet
                return Response({'message': 'Webhook processed'}, status=status.HTTP_200_OK)
            except Exception as e:
                # Log the error in production
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetOrderUnfinished(generics.ListAPIView): # lấy các order chưa hoàn thành
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    pagination_class = LargePagePagination
    def get_queryset(self):
        user_id = self.request.user.id
        return get_order_pending(user_id=user_id)

class WithdrawMoney(APIView):
    """
    User nhập số tiền muốn rút → validate → trừ wallet → tạo WithdrawRequest
    → Celery task gọi SePay chuyển tiền ra bank(thành công thì status completed còn fail thì refund tiền đúng bằng amount của withdraw request)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        #user nhập amount -> APIView -> serializer validate data truyền vào là amount -> APIView
        serializer = WithdrawRequestSerializer(data=request.data) # user nhập và lấy ra tiền sau validate serializer(cách dùng serializer trong api view)
        serializer.is_valid(raise_exception=True)

        try: # check user phải có page
            page = request.user.profile.page
        except AttributeError:
            return Response(
                {'error': 'Bạn chưa có Page. Vui lòng tạo Page trước khi rút tiền.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try: # tạo request, trừ tiền và chạy celery rút
            wr = create_withdrawrq(
                page_id=page.id,
                amount=serializer.validated_data['amount'],
            )
            return Response({
                'withdraw_request_id': wr.withdraw_request_id,
                'amount': wr.amount,
                'bank_account_number': wr.bank_account_number,
                'bank_code': wr.bank_code,
                'status': wr.status,
                'message': 'Yêu cầu rút tiền đã được ghi nhận và đang xử lý.',
            }, status=status.HTTP_201_CREATED)

        except DjangoValidationError as e:
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)

class WithdrawHistoryView(generics.ListAPIView):
    """Lịch sử các lần rút tiền của page."""
    permission_classes = [IsAuthenticated]
    serializer_class = WithdrawSerializer
    pagination_class = LargePagePagination

    def get_queryset(self):
        page = self.request.user.profile.page
        return WithdrawRequest.objects.filter(page=page).order_by('-created_at')