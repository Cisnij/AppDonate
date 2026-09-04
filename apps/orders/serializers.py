from rest_framework import serializers

from apps.users.serializers import ProfileSerializer, PageSerializer
from .models import *

class OrderSerializer(serializers.ModelSerializer): #order để hiển thị
    donater = ProfileSerializer(source='donater.profile',read_only=True)
    donatee_page = PageSerializer(read_only=True)
    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ["order_id","status",'created_at','expired_at']

class TransactionSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ["id", "order", "bank_transaction_id", "success_time", "amount"]

class WithdrawSerializer(serializers.ModelSerializer): # dùng để hiển thị lịch sử rút tiền
    class Meta:
        model = WithdrawRequest
        fields = "__all__"
        read_only_fields = ["user", "withdraw_request_id", "status", "created_at"]

'''serializer tự khai báo k dựa vào model'''
class WithdrawRequestSerializer(serializers.Serializer): # validate đầu vào khi điển số tiền rút
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=0,
        required=True,
        min_value=10000,  # rút tối thiểu 50,000đ
    )

    def validate_amount(self, value):
        # Đảm bảo là số nguyên (VND không có xu)
        if value != value.to_integral_value(): #intergral là giá trị không có số lẻ
            raise serializers.ValidationError("Số tiền phải là số nguyên (VND).")
        return value

class CreateOrderSerializer(serializers.Serializer): #validate đầu vào khi tạo
    page_id = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True, min_value=1000)
    content = serializers.CharField(max_length=255, required=False, allow_blank=True, default='')

class WebhookSerializer(serializers.Serializer): #validate đầu vào cuả webhook gọi tới
    order_id = serializers.UUIDField(required=True)
    transaction_id = serializers.CharField(max_length=100, required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    status = serializers.CharField(max_length=20, required=True)