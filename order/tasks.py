import logging

import requests
from celery import shared_task
from channels.layers import get_channel_layer
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from asgiref.sync import async_to_sync
from order.models import Order, WithdrawRequest
from user.models import Wallet

logger = logging.getLogger(__name__)


@shared_task
def expire_pending_orders_task():  # lấy thời gian hiện tại và xem order nào có thgian expired bé hơn hiện tại thì dọn

    now = timezone.now()
    expired_orders = Order.objects.filter(status='Pending', expired_at__lte=now) #lấy ra order hết hạn
    updated_count = expired_orders.update(status='Expired') # cập nhật ordor hết hạn thành expired
    return f"Expired {updated_count} orders"


@shared_task
def broadcast_donation_task(page_id, donation_data):  # lấy page id và data để push tới route ws đó
    """
    Task to broadcast a successful donation to a specific page's websocket group.
    donation_data is a dict containing details like amount, donater_name, content, etc.
    """
    channel_layer = get_channel_layer()
    group_name = f'notification_{page_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send_notification',
            'data': donation_data
        }
    )
    return f"Broadcasted to {group_name}"


@shared_task(bind=True, max_retries=3, default_retry_delay=60, )  # thử lại sau 60s nếu lỗi mạng
def process_withdrawal_task(self, withdraw_request_id: str):
    """
    Celery task gọi SePay Money Transfer API để chuyển tiền ra bank.
    Chạy ngoài DB transaction để tránh lock quá lâu.
    """

    try:
        wr = WithdrawRequest.objects.get(withdraw_request_id=withdraw_request_id)  # lấy ra request
    except WithdrawRequest.DoesNotExist:
        logger.error(f"[Withdraw] WithdrawRequest {withdraw_request_id} not found")
        return

    if wr.status != WithdrawRequest.STATUS_PENDING:  # nếu status là đã hết hạn hoặc đã thành công thì không thực thi
        logger.warning(f"[Withdraw] {withdraw_request_id} already {wr.status}, skip")
        return

    sepay_api_url = getattr(settings, 'SEPAY_TRANSFER_URL', 'https://my.sepay.vn/api/v1/transfer')
    sepay_token = getattr(settings, 'SEPAY_API_TOKEN', '')

    payload = {
        'bank_code': wr.bank_code,
        'account_number': wr.bank_account_number,
        'account_name': wr.bank_account_name,
        'amount': wr.amount,
        'description': f'AppDonate withdraw {str(wr.withdraw_request_id)[:8]}',
        'reference_id': str(wr.withdraw_request_id),
    }

    # gọi tới api của sepay thực hiện chuyển tiền từ tài khoản app
    try:
        response = requests.post(
            sepay_api_url,
            json=payload,
            headers={
                'Authorization': f'Bearer {sepay_token}',
                'Content-Type': 'application/json',
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()  # sepay trả về data

        # SePay trả về transaction_id khi thành công, cập nhật withdraw request gồm status và transaction id
        sepay_txn_id = data.get('transaction_id') or data.get('data', {}).get('transaction_id', '')

        wr.status = WithdrawRequest.STATUS_COMPLETED
        wr.sepay_transaction_id = sepay_txn_id
        wr.completed_at = timezone.now()
        wr.save(update_fields=['status', 'sepay_transaction_id', 'completed_at'])
        logger.info(f"[Withdraw] {withdraw_request_id} COMPLETED, sepay_txn={sepay_txn_id}")

    except requests.exceptions.Timeout as exc:  # disconnect thì retry lần 1
        logger.warning(f"[Withdraw] {withdraw_request_id} timeout, retrying...")
        raise self.retry(exc=exc)

    except requests.exceptions.RequestException as exc:
        # Lỗi mạng/SePay → retry
        logger.error(f"[Withdraw] {withdraw_request_id} request error: {exc}")
        raise self.retry(exc=exc)

    except Exception as exc:  # retry lần 3 k đc thì refund
        # Lỗi không mong đợi thì đánh dấu FAILED, không retry
        logger.exception(f"[Withdraw] {withdraw_request_id} unexpected error: {exc}")

        # Hoàn tiền vào wallet, try/except k có revert khi fail
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(profile=wr.page.profile)  # lock row
            wallet.balance += wr.amount  # add đúng bằng số tiền từ request
            wallet.save(update_fields=['balance'])

        # update status fail
        wr.status = WithdrawRequest.STATUS_FAILED
        wr.failure_reason = str(exc)
        wr.save(update_fields=['status', 'failure_reason'])
