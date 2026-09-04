from django.urls import path
from .views import DonateForPage, BankWebhookAPIView, GetOrderUnfinished, UserDonateHistory, WithdrawMoney, WithdrawHistoryView

urlpatterns = [
    path('order/donate/<int:page_id>/', DonateForPage.as_view(), name='donate-for-page'),
    path('order/webhook/', BankWebhookAPIView.as_view(), name='bank-webhook'),
    path('order/pending/', GetOrderUnfinished.as_view(), name='pending-orders'),
    path('order/history/', UserDonateHistory.as_view(), name='donate-history'),
    path('order/withdraw/', WithdrawMoney.as_view(), name='withdraw-money'),
    path('order/withdraw/history/', WithdrawHistoryView.as_view(), name='withdraw-history'),
]
