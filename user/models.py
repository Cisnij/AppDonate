from django.contrib.auth.models import User
from django.db import models
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE_CASCADE
# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='default.jpg', upload_to='profile_pics')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    phone_number = models.CharField(max_length=11,blank=True,null=True)
    birth =models.DateField(blank=True,null=True)
    verified = models.BooleanField(default=False)
    auth_provider = models.CharField(max_length=20, default='email')  # 'email' hoặc 'google'
    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Page(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    page_name = models.CharField(max_length=100)
    description = models.TextField()
    is_legit = models.BooleanField(default=False)
    is_active =models.BooleanField(default=True)
    total_received = models.DecimalField(max_digits=15, decimal_places=0, default=0)

    withdraw_bank_account_number = models.CharField(max_length=50, blank=True)
    withdraw_bank_account_name = models.CharField(max_length=100, blank=True)
    withdraw_bank_code = models.CharField(max_length=20, blank=True)
    
    bank_code = models.CharField(max_length=20) #VCB/MBB
    def __str__(self):
        return f'{self.page_name}'
    class Meta:
        indexes = [models.Index(fields=['is_legit','is_active'])]

class Wallet(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=15, decimal_places=0, default=0)
    updated_at = models.DateTimeField(auto_now=True)