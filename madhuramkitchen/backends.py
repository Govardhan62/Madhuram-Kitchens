# myapp/backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from phonenumbers import parse, is_valid_number

UserModel = get_user_model()

class PhoneEmailBackend(ModelBackend):
    def authenticate(self, request, phone_number=None, email=None, password=None, otp=None, **kwargs):
        if phone_number:
            try:
                phone_number = parse(phone_number, None)
                if not is_valid_number(phone_number):
                    return None
                # Add your OTP verification logic here
                user = UserModel.objects.get(phone_number=phone_number)
                # Verify OTP
                if otp == '123456':  # Dummy OTP for demonstration
                    return user
            except UserModel.DoesNotExist:
                return None
        elif email:
            try:
                user = UserModel.objects.get(email=email)
                if user.check_password(password):
                    return user
            except UserModel.DoesNotExist:
                return None
        return None

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
