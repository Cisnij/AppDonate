from django.db.models import QuerySet

from .models import *

def get_block(page_id:int)->QuerySet[Block]:
    return Block.objects.filter(blocker_id=page_id)

def is_blocked(* ,page_id :int, user_id :int )-> bool:
    return Block.objects.filter(blocker_id=page_id, blockee_id=user_id).exists()

def get_blocked_ids(*, user_id:int)->list:
    blocked_ids = list(Block.objects.filter(blocked_id=user_id).values_list("blocker_id", flat=True))  # người đã block mình
    return blocked_ids

def check_block(*,page_id: int,user_id: int) -> Block | None:
    return Block.objects.filter(
        blocker_id=page_id,
        blockee_id=user_id,
    ).first()