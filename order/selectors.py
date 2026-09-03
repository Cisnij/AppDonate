from django.db.models import QuerySet

from .models import Transaction, Order


def get_user_transaction(*,user_id:int)->QuerySet[Transaction]: # lấy tất cả lịch sử donate thành công cuả user
    transactions = Transaction.objects.filter(donater_id=user_id)
    return transactions

def get_order_pending(*,user_id:int)->QuerySet[Order]: # lấy tất cả lịch sử donate đang chờ hoàn thành
    orders = Order.objects.filter(donater_id=user_id,status="Pending")
    return orders