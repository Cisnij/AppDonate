import uuid
from django.db import models
from apps.users.models import Page,Profile,User
# Create your models here.
from safedelete.models import SOFT_DELETE_CASCADE,SOFT_DELETE
from safedelete.models import SafeDeleteModel

class Order(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    status_choices=[
        ('Pending','Pending'),
        ('Completed','Completed'),
        ('Expired','Expired'),
    ]
    donater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_sent')
    donatee_page = models.ForeignKey(Page, on_delete=models.CASCADE,related_name='orders_received')
    order_id = models.UUIDField(default=uuid.uuid4, editable=False,primary_key=True,unique=True)
    content = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(choices=status_choices, default='Pending',max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes=[models.Index(fields=['status','expired_at'])]

class Transaction(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    order =models.OneToOneField(Order, on_delete=models.CASCADE)
    bank_transaction_id = models.CharField(max_length=100, unique=True)  # order id là để tạo nội dung cho mã qr và ngân hàng trả lại order_id này để update đúng bảng, còn bank transaction id là id giao dịch của ngân hàng
    success_time = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    donater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions_sent')
    donatee_page = models.ForeignKey(Page, on_delete=models.CASCADE,related_name='transactions_received')
    class Meta:
        indexes = [
            models.Index(fields=['donatee_page', '-success_time']),
            models.Index(fields=['donater', '-success_time']),
        ]

class WithdrawRequest(SafeDeleteModel):
    status_choices=[
        ('Pending','Pending'),
        ('Completed','Completed'),
        ('Expired','Expired'),
    ]
    _safedelete_policy = SOFT_DELETE_CASCADE
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='withdraw_requests')
    withdraw_request_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    amount = models.DecimalField(max_digits=15, decimal_places=0)
    status = models.CharField(choices=status_choices, default='Pending', max_length=20)

    # Thông tin bank nhận ngay tại thời điểm rút để user có thể xem lại(nếu đã đổi tkhoan)
    bank_account_number = models.CharField(max_length=50)
    bank_account_name = models.CharField(max_length=100)
    bank_code = models.CharField(max_length=20)

    # SePay response
    sepay_transaction_id = models.CharField(max_length=100, blank=True, null=True) # id giao dịch sau khi chuyển tiền tới page đó
    failure_reason = models.TextField(blank=True, null=True) #lý do fail
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['page', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Withdraw {self.amount} from {self.page} [{self.status}]"