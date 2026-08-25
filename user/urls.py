from django.contrib import admin
from django.urls import path,include
from .views import *
urlpatterns = [
    path('api/profile/',ProfileModify.as_view(),name='api_profile'),
    path('api/private-profile/',PrivateProfileModify.as_view(),name='api_private_profile'),
    path('api/page/', PageModify.as_view(), name='api_page'),
    path('api/private-page/', PrivatePageModify.as_view(), name='api_private_page'),
    path('api/page/<int:page_id>/', PageView.as_view(), name='api_page_view'),
]
