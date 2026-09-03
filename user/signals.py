from allauth.account.signals import email_confirmed, user_logged_in
from django.dispatch import receiver

from user.models import Profile, Wallet


@receiver(email_confirmed)
def update_profile(sender, request, email_address, **kwargs):
    user = email_address.user
    profile = user.profile
    profile.verified=True
    profile.save(update_fields=['verified'])

@receiver(email_confirmed)
def add_wallet(sender, request, email_address, **kwargs):
    user = email_address.user
    if hasattr(user, 'profile') and not hasattr(user.profile, 'wallet'):
        Wallet.objects.create(profile=user.profile)
