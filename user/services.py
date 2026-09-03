from .selectors import get_profile_or_400, get_user_or_400


def update_profile(*, user_id : int, data : dict)-> None:
    user = get_user_or_400(user_id=user_id)
    email = data.get('email')
    phone_number = data.get('phone_number')
    if email is not None:
        user.email = email
        user.save(update_fields=['email'])
    if phone_number is not None:
        user.phone_number = phone_number
        user.save(update_fields=['phone_number'])

from .models import Page, Wallet
from django.db import transaction

def create_page(*, profile, data: dict) -> Page:
    if hasattr(profile, 'page'):
        raise Exception("Profile already has a page.")
        
    with transaction.atomic():
        page = Page.objects.create(
            profile=profile,
            page_name=data.get('page_name'),
            description=data.get('description', ''),
            bank_code=data.get('bank_code', ''),
            withdraw_bank_account_number=data.get('withdraw_bank_account_number', ''),
            withdraw_bank_account_name=data.get('withdraw_bank_account_name', ''),
            withdraw_bank_code=data.get('withdraw_bank_code', '')
        )
        if not hasattr(profile, 'wallet'):
            Wallet.objects.create(profile=profile)
            
    return page

def delete_page(*, page: Page) -> None:
    page.delete()

