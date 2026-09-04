from django.db import models
from apps.users.models import User,Page,Profile
# Create your models here.
class Block(models.Model):
    blocker = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='blocked_users')
    blockee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by_pages')
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('blocker', 'blockee')
        indexes = [
            models.Index(fields=['blocker', 'blockee']),
        ]


class SavePage(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    page = models.ForeignKey(Page,on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'page')