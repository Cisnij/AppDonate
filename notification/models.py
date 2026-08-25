from django.db import models
from user.models import User,Page
from order.models import Transaction
# Create your models here.

class Notification(models.Model):
    donater = models.ForeignKey(User,on_delete=models.CASCADE)
    donatee = models.ForeignKey(Page,on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    transaction= models.OneToOneField('Transaction',on_delete=models.CASCADE)
    class Meta:
        indexes = [
            models.Index(fields=['donater','created_at']),
            models.Index(fields=['donatee', 'created_at'])
        ]

