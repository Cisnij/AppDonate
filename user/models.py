from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='default.jpg', upload_to='profile_pics')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    phone_number = models.CharField(max_length=11)
    birth =models.DateField()
    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Page(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    page_name = models.CharField(max_length=100)
    description = models.TextField()
    is_legit = models.BooleanField(default=False)
    is_active =models.BooleanField(default=True)
    current_amount = models.IntegerField(default=0)
    accumulated_amount = models.IntegerField(default=0)
    bank_account_number = models.CharField(max_length=50)
    bank_account_name = models.CharField(max_length=100)
    bank_code = models.CharField(max_length=20) #VCB/MBB
    def __str__(self):
        return f'{self.page_name}'
    class Meta:
        indexes = [models.Index(fields=['is_legit','is_active'])]