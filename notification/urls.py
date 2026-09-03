from django.contrib import admin
from django.urls import path,include
from .views import *
urlpatterns = [
    path('api/notifications/',NotificationListView.as_view(),name='notification-page'),

]
