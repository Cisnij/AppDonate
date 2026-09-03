from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError

from order.models import Order, Transaction, WithdrawRequest
from user.models import Wallet, Page
from relationship.selectors import is_blocked
from order.tasks import broadcast_donation_task

#tạo order
def create_order(*, user_id: int, page_id: int, amount: Decimal, content: str) -> Order:
    if is_blocked(page_id=page_id, user_id=user_id):
        raise ValidationError("Bạn đã bị chặn bởi page này.")
        
    return Order.objects.create(
        donater_id=user_id,
        donatee_page_id=page_id,
        amount=amount,
        status='Pending',
        content=content,
        expired_at=timezone.now() + timedelta(minutes=15),
    )

#tạo mã qr dựa vào số ngân hàng của bên thứ 3(là chính app) dựa vào order đã tạo(logic: tạo order -> tạo mã)
def generate_vietqr_url(order: Order) -> str:
    bank_code = getattr(settings, 'PLATFORM_BANK_CODE', 'MB')
    account_no = getattr(settings, 'PLATFORM_BANK_ACCOUNT', '')
    account_name = getattr(settings, 'PLATFORM_BANK_ACCOUNT_NAME', '')
    
    amount = int(order.amount)
    add_info = str(order.order_id)
    
    url = f"https://img.vietqr.io/image/{bank_code}-{account_no}-compact2.png?amount={amount}&addInfo={add_info}&accountName={account_name}"
    return url


# xử lý transaction của webhook khi đc gọi tới(câp nhật order, tạo data transaction)
@transaction.atomic
def process_bank_webhook(data: dict) -> None:
    order_id = data.get('order_id')
    transaction_id = data.get('transaction_id')
    amount = data.get('amount')
    status = data.get('status')

    if not all([order_id, transaction_id, amount]) or status != 'SUCCESS': # nếu k trả về đầy đủ field hoặc trả về trạng thái lỗi thì k cập nhật
        return

    try:
        order = ( # khóa cột select for update để tránh lỗi dữ liệu(select for update khóa trong suốt transaction
            Order.objects
            .select_for_update()
            .select_related('donater__profile', 'donatee_page__profile')
            .get(order_id=order_id, status='Pending')
        )

        if amount != order.amount: # nếu amount ngân hàng gửi tới khác amount trong order tạo lúc đầu thì lỗi
            raise ValidationError(f"Amount mismatch: expected {order.amount}, got {amount}")

        order.status = 'Completed'
        order.save(update_fields=['status'])

        #tạo transaction dựa vào order thành công
        Transaction.objects.create(
            order=order,
            bank_transaction_id=transaction_id,
            amount=amount,
            donater_id=order.donater_id,
            donatee_page_id=order.donatee_page_id
        )

        # khóa cột trong wallet và update tiền thêm vào
        wallet, _ = Wallet.objects.select_for_update().get_or_create(
            profile=order.donatee_page.profile
        )
        wallet.balance += amount
        wallet.save(update_fields=['balance'])

        # thực hiẹn gọi tới celery chạy broad cast qua websocket
        donater_profile = order.donater.profile
        donation_data = {
            'donater_name': f"{donater_profile.first_name} {donater_profile.last_name}",
            'amount': str(amount),
            'content': order.content or '',
        }
       # vì đang bọc trong transaction nên cần transaction commit hoàn thành thì mới gọi celery push, nếu chưa hoàn thành chưa có db mà push thì lỗi(có thẻ đem ra ngoài transaction để k dùng)
        transaction.on_commit(
            lambda: broadcast_donation_task.delay(order.donatee_page_id, donation_data)
        )

    except Order.DoesNotExist:
        # Order doesn't exist or is no longer Pending — ignore silently
        pass
        
@transaction.atomic
def create_withdrawrq(*, page_id: int, amount: Decimal) -> WithdrawRequest:
    """
    Tạo yêu cầu rút tiền:
      1. Lock wallet để tránh race condition
      2. Validate số dư
      3. Trừ tiền ra khỏi wallet
      4. Tạo WithdrawRequest (Pending)
      5. Sau khi commit → dispatch Celery task gọi SePay
    """
    from order.tasks import process_withdrawal_task

    # Lấy ra page và thông tin bank từ page đó đã điền
    page = (
        Page.objects
        .select_related('profile')
        .get(id=page_id)
    )

    # Nếu page chưa cập nhật thêm thông tin rút tiền
    if not page.withdraw_bank_account_number or not page.withdraw_bank_code:
        raise ValidationError(
            "Vui lòng cấu hình thông tin tài khoản ngân hàng rút tiền trong cài đặt."
        )

    # lấy wallet của page, Lock wallet thực thi update
    wallet = Wallet.objects.select_for_update().get(profile=page.profile)

    #so sánh số dư trong ví của page đó nếu bé hơn số tiền yêu cầu rút thì lỗi
    if wallet.balance < amount:
        raise ValidationError(
            f"Số dư không đủ. Hiện có: {wallet.balance:,.0f}đ, yêu cầu rút: {amount:,.0f}đ"
        )

    #  Trừ tiền
    wallet.balance -= amount
    wallet.save(update_fields=['balance'])

    # tạo withdraw request
    wr = WithdrawRequest.objects.create(
        page=page,
        amount=amount,
        status=WithdrawRequest.STATUS_PENDING,
        bank_account_number=page.withdraw_bank_account_number, # gắn stk tại thời điểm tạo
        bank_account_name=page.withdraw_bank_account_name,
        bank_code=page.withdraw_bank_code,
    )

    # thực thi celery chạy lệnh rút ngân hàng
    transaction.on_commit(
        lambda: process_withdrawal_task.delay(str(wr.withdraw_request_id))
    )

    return wr