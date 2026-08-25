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


