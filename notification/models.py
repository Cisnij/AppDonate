from django.db import models
from user.models import User,Page
from order.models import Transaction
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE

class Notification(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    donater = models.ForeignKey(User,on_delete=models.CASCADE)
    donatee = models.ForeignKey(Page,on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    transaction= models.OneToOneField('order.Transaction',on_delete=models.CASCADE) # import từ folder order, lấy bảng order.Transaction
    class Meta:
        indexes = [
            models.Index(fields=['donater','created_at']),
            models.Index(fields=['donatee', 'created_at'])
        ]

