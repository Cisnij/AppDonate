from apps.relationships.exceptions import AlreadyBlocked, Is_Page, BlockNotFound
from apps.relationships.models import Block
from apps.relationships.selectors import is_blocked, check_block


def create_block(*, user_id: int, page_id: int ) -> Block:
    blocked = is_blocked(page_id=page_id, user_id=user_id)
    if not page_id:
        raise Is_Page()
    if blocked:
        raise AlreadyBlocked()
    Block.objects.create(
        blocker_id=page_id,
        blockee_id=user_id,
    )

def remove_block(*,user_id: int,page_id: int | None) -> None:
    if not page_id:
        raise Is_Page()

    block = check_block(page_id=page_id,user_id=user_id,)

    if not block:
        raise BlockNotFound()

    block.delete()