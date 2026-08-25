from django.contrib.auth.models import User
from rest_framework.generics import get_object_or_404
from .models import Profile, Page


def get_user_profile(* ,user_id:int )-> Profile:
    return get_object_or_404(Profile.objects.select_related('page'), user_id=user_id)

def get_profile_or_400(* ,profile_id:int )-> Profile:
    return get_object_or_404(Profile.objects.select_related('page'), id=profile_id)

def get_user_or_400(* ,user_id:int )-> User:
    return get_object_or_404(User.objects.select_related('profile'), id=user_id)

def get_user_page(* ,user_id:int )-> Page:
    return get_object_or_404(Page.objects.select_related('profile'), id=user_id)

def get_page(* ,page_id :int )-> Page:
    return get_object_or_404(Page.objects.select_related('profile'), id=page_id)