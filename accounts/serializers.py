from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField

from .models import User


class GetAdminUserSerializer(serializers.ModelSerializer):
    phone = serializers.SerializerMethodField('get_phone')
    image = serializers.SerializerMethodField('get_image_url')
    age = serializers.SerializerMethodField('get_age')

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'phone',
            'name',
            'gender',
            'image',
            'created_at',
            'is_admin',
            'special_role',
            'is_superuser',
            'age',
            'date_of_birth',
            'address',
            'last_login',
            'slug',
            "marital_status"
        )

    def get_age(self, admin_user):
        return admin_user.get_age()

    def get_phone(self, admin_user):
        return str(admin_user.phone.as_national)

    def get_image_url(self, admin_user):
        return admin_user.get_image_url


class CreateAdminUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = (
            'email',
            'address',
            'phone',
            'name',
            'gender',
            'image',
            'special_role',
            'password',
            'password2',
            'date_of_birth',
            'marital_status'
        )
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'},
                'trim_whitespace': False
            }
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            error_message = {"password2": _("Password fields didn't match.")}
            raise serializers.ValidationError(error_message)

        # Validate password strength
        password = data['password']
        errors = {}
        try:
            validate_password(password, self.instance)
        except ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)
        return data

    def save(self, **kwargs):
        self.validated_data.pop('password2', None)
        user_data = self.validated_data
        user = super().save(**kwargs)
        user.set_password(user_data['password'])
        user.is_admin = True
        user.save()
        return user


class LoginAdminSerializer(serializers.Serializer):
    phone = PhoneNumberField(region='CM')
    password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        phone = attrs.get('phone', '')
        password = attrs.get('password', '')
        user = authenticate(request=self.context.get(
            'request'), phone=phone, password=password)

        if not user:
            raise serializers.ValidationError(
                _("Invalid phone number or password."), code='authorization')

        if not user.is_active:
            raise serializers.ValidationError(
                _("User account is inactive."), code='inactive')

        if not user.is_admin:
            raise serializers.ValidationError(
                _("Access restricted to administrators only."), code='unauthorized')

        attrs['user'] = user
        return attrs


class ChangeAdminPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True, trim_whitespace=False)
    new_password1 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True, trim_whitespace=False)
    new_password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        user = self.context.get('user')
        old_password = attrs.get('old_password')
        if not user.check_password(old_password):
            msg = {'old_password': _("Wrong password.")}
            raise serializers.ValidationError(msg)

        if attrs['new_password1'] != attrs['new_password2']:
            error_message = {"new_password2": _(
                "The two new passwords do not match.")}
            raise serializers.ValidationError(error_message)

        # Validate new password strength using Django's built-in validators
        new_password = attrs['new_password1']
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            raise serializers.ValidationError(
                {'new_password1': list(e.messages)})

        return attrs


class ChangeAdminPasswordSerializerBySuperUser(serializers.Serializer):
    new_password1 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True, trim_whitespace=False)
    new_password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        if attrs['new_password1'] != attrs['new_password2']:
            error_message = {"new_password2": _(
                "The two new passwords do not match.")}
            raise serializers.ValidationError(error_message)

        # Validate new password strength using Django's built-in validators
        new_password = attrs['new_password1']
        try:
            validate_password(new_password, self.context.get('user'))
        except ValidationError as e:
            raise serializers.ValidationError(
                {'new_password1': list(e.messages)})

        return attrs


class UpdateAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'phone',
            'name',
            'gender',
            'email',
            'special_role',
            'marital_status',
            'date_of_birth',
            'address'
        ]


class ChangeAdminImageSerializer(serializers.Serializer):
    image = serializers.ImageField()
