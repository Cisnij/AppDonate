from django.utils import timezone

from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import transaction
from django.core.cache import cache
from rest_framework import serializers
from allauth.account.models import EmailAddress
from user.models import Profile
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from allauth.socialaccount.models import SocialAccount
from phonenumber_field.serializerfields import PhoneNumberField


'''khi người dùng nhập, gọi api nó sẽ lấy giá trị và validate sau đó mới lưu vào csdl là flow của serializer đúng k'''

name_validator = RegexValidator(
    regex=r'^[a-zA-ZÀ-ỹ\s]+$', # check các kí tự này chỉ đc từ a-Z và dấu
    message='Tên chỉ được chứa chữ cái và khoảng trắng' # báo lỗi
)
class CustomRegisterSerializer(RegisterSerializer): # Sửa chức năng register nên RegisterSerializer
    username=None #Bỏ username đi
    firstname=serializers.CharField(required=True, allow_blank=False,validators=[name_validator]) #thêm first name
    lastname=serializers.CharField(required=True, allow_blank=False, validators=[name_validator]) #thêm last name
   
    _has_phone_field = True #thêm số điện thoại
    phone_number = PhoneNumberField(required=True)
    birthday=serializers.DateField(required=True) #thêm ngày sinh

    def validate_birthday(self, value):  # validate riêng cho birthday
        if value > timezone.now().date():
            raise serializers.ValidationError('Ngày sinh không thể là tương lai')
        if value.year < 1900:
            raise serializers.ValidationError('Ngày sinh không hợp lệ')
        return value


    def get_cleaned_data(self): #sau khi xác thực thì lấy cái giá trị mới xác thực gán cho giá trị chính và lưu , cái này là chỉ gán các field có sẵn trong user, muốn thêm field tự custome thì overide save()
        clean_data=super().get_cleaned_data() #clean data là dữ liệu chính và được gán vào dữ liệu vừa validate
        clean_data['first_name'] = self.validated_data.get('firstname', '')
        clean_data['last_name'] = self.validated_data.get('lastname', '')
        clean_data['username'] = self.validated_data.get('email', '') #gán email vào username
        return clean_data

    def save(self, request):
        user = super().save(request)
        Profile.objects.create(
            user=user,
            first_name=self.validated_data.get('firstname', ''),
            last_name=self.validated_data.get('lastname', ''),
            email=self.validated_data.get('email', ''),
            phone_number=str(self.validated_data.get('phone_number', '')),
            birth=self.validated_data.get('birthday'),
            verified=False,  # mặc định chưa verify, đúng field bạn đã có
        )
        return user

class CustomeLoginSerializer(LoginSerializer): #Sửa chức năng login nên LoginSerializer
    username=None #bỏ username đi
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if not email or not password:
            raise serializers.ValidationError("Email and password are required")
        user = authenticate(request=self.context.get('request'),username=email,password=password) # trả ra user

        if not user:
            raise serializers.ValidationError("Thông tin đăng nhập không hợp lệ")
        if not user.is_active:
            raise serializers.ValidationError("Người dùng này chưa được kích hoạt")
        
        email_verified=EmailAddress.objects.filter(user=user, email=email).first()
        if email_verified and not email_verified.verified:
            raise serializers.ValidationError("Email is not verified.")

        attrs['user'] = user # gán user sau khi validate 
        return attrs

