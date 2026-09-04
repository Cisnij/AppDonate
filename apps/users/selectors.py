from django.contrib.auth.models import User
from rest_framework.generics import get_object_or_404
from .models import Profile, Page, Wallet
from apps.relationships.models import Block

def get_user_profile(* ,user_id:int )-> Profile:
    return get_object_or_404(Profile.objects.select_related('page'), user_id=user_id)

def get_profile_or_400(* ,profile_id:int )-> Profile:
    return get_object_or_404(Profile.objects.select_related('page'), id=profile_id)

def get_user_or_400(* ,user_id:int )-> User:
    return get_object_or_404(User.objects.select_related('profile','profile__page'), id=user_id)

def get_user_page(* ,user_id:int )-> Page:
    return get_object_or_404(Page.objects.select_related('profile'), id=user_id)

def get_page(* ,page_id :int )-> Page:
    return get_object_or_404(Page.objects.select_related('profile'), id=page_id)

def get_user_wallet(* ,user_id :int )-> Wallet:
    return get_object_or_404(Wallet, user_id=user_id)

from rest_framework.exceptions import PermissionDenied

def get_page_for_user(*, page_id: int, viewer_user: User) -> Page:
    page = get_page(page_id=page_id)
    if viewer_user.is_authenticated:
        if Block.objects.filter(blocker=page, blockee=viewer_user).exists():
            raise PermissionDenied("You are blocked from viewing this page.")
    return page
