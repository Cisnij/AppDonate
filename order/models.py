import uuid
from django.db import models
from user.models import Page,Profile,User
# Create your models here.

class Order(models.Model):
    status_choices=[
        ('Pending','Pending'),
        ('Completed','Completed'),
        ('Expired','Expired'),
    ]
    donater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_sent')
    donatee_page = models.ForeignKey(Page, on_delete=models.CASCADE,related_name='orders_received')
    order_id = models.UUIDField(default=uuid.uuid4, editable=False,primary_key=True,unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(choices=status_choices, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes=[models.Index(fields=['status','expired_at'])]

class Transaction(models.Model):
    order =models.OneToOneField(Order, on_delete=models.CASCADE)
    bank_transaction_id = models.CharField(max_length=100, unique=True)  # order id là để tạo nội dung cho mã qr và ngân hàng trả lại order_id này để update đúng bảng, còn bank transaction id là id giao dịch của ngân hàng
    success_time = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    donater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions_sent')
    donatee_page = models.ForeignKey(Page, on_delete=models.CASCADE,related_name='transactions_received')
    class Meta:
        models.Index(fields=['donatee_page', '-created_at']),
        models.Index(fields=['donater', '-created_at']),