from .models import *
from rest_framework import serializers

class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    birth = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = ('user','avatar', 'first_name', 'last_name', 'email', 'phone_number','birth')
        read_only_fields = ('user')
    def get_email(self,obj):
        request =self.context.get('request')
        if request and request.user.is_authenticated and request.user == obj.user:
            return obj.email
        return None
    def get_phone_number(self,obj):
        request =self.context.get('request')
        if request and request.user.is_authenticated and request.user == obj.user:
            return obj.phone_number
        return None
    def get_birth(self,obj):
        request =self.context.get('request')
        if request and request.user.is_authenticated and request.user == obj.user:
            return obj.birth
        return None

class PrivateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('email', 'phone_number','birth')

class PageSerializer(serializers.ModelSerializer):
    profile =ProfileSerializer(source='profile.page',read_only=True)
    accumulated_amount = serializers.SerializerMethodField()
    withdraw_bank_account_number = serializers.SerializerMethodField()
    withdraw_bank_account_name = serializers.SerializerMethodField()
    withdraw_bank_code = serializers.SerializerMethodField()
    class Meta:
        model = Page
        fields = "__all__"
        read_only_fields = ('profile','is_legit','is_active','accumulated_amount','withdraw_bank_account_number','withdraw_bank_account_name','withdraw_bank_code')
    def get_accumulated_amount(self,obj):
        request =self.context.get('request')
        if request and request.user.is_authenticated and request.user == obj.profile.user:
            return obj.accumulated_amount
        return None
    def get_withdraw_bank_account_number(self,obj):
        request =self.context.get('request')
        if request and request.user.is_authenticated and request.user == obj.profile.user:
            return obj.withdraw_bank_account_number
        return None
    def get_withdraw_bank_account_name(self,obj):
        request =self.context.get('request')
        if request and request.user.is_authenticated and request.user == obj.profile.user:
            return obj.withdraw_bank_account_name
        return None
    def get_withdraw_bank_code(self,obj):
        request =self.context.get('request')
        if request and request.user.is_authenticated and request.user == obj.profile.user:
            return obj.withdraw_bank_code
        return None

class PrivatePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('current_amount','accumulated_amount','bank_account_number','bank_account_name','bank_code')

class WalletSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(source='user.profile',read_only=True)
    class Meta:
        model = Wallet
        fields = "__all__"
        read_only_fields = ('user','balance')