from django.contrib.auth import authenticate
from django.utils.translation import gettext as _
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from accounts.models import User

from .models import Teacher


class GetTeacherSerializer(serializers.ModelSerializer):
    phone = serializers.SerializerMethodField('get_phone')
    department = serializers.SerializerMethodField('get_department')
    age = serializers.SerializerMethodField('get_age')
    image = serializers.SerializerMethodField('get_image_url')

    def get_department(self, teacher):
        return {
            'id': teacher.department.id,
            'name': teacher.department.name,
            'slug': teacher.department.slug,
        }

    def get_age(self, teacher):
        return teacher.get_age()

    def get_image_url(self, teacher):
        return teacher.get_image_url

    def get_phone(self, teacher):
        return str(teacher.phone.as_national)

    class Meta:
        model = Teacher
        fields = (
            'id',
            'phone',
            'username',
            'gender',
            'email',
            'image',
            'address',
            'date_of_birth',
            'department',
            'age',
            'is_hod',
            'is_teacher',
            'marital_status',
            'title_name',
            'name',
            'slug',
            'last_login'
        )


class CreateTeacherSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    class Meta:
        model = Teacher
        fields = ['email',
                  'phone',
                  'name',
                  'gender',
                  'image',
                  'password',
                  'password2',
                  'address',
                  'date_of_birth',
                  'department',
                  'is_hod',
                  'marital_status',
                  'title_name',
                  'username'
                  ]
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}}
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
        teacher_data = self.validated_data
        teacher = super().save(**kwargs)
        teacher.set_password(teacher_data['password'])
        teacher.save()
        return teacher


class UpdateTeacherSerializer(serializers.ModelSerializer):

    class Meta:
        model = Teacher
        fields = (
            'name',
            'phone',
            'username',
            'gender',
            'email',
            'address',
            'date_of_birth',
            'marital_status',
            'title_name',
            'username',
        )


class ChangeTeacherPasswordBySuperUserSerializer(serializers.Serializer):
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


class ChangeTeacherImageSerializer(serializers.Serializer):
    image = serializers.ImageField()


class LoginTeacherSerializer(serializers.Serializer):
    phone = PhoneNumberField(region='CM')
    password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        phone = attrs.get('phone', '')
        password = attrs.get('password', '')

        admin = User.objects.filter(is_admin=True, phone=phone)

        if admin.exists():
            raise serializers.ValidationError(
                _("Access restricted to teachers only."), code='unauthorized')

        try:
            teacher = Teacher.objects.get(phone=phone)
        except Teacher.DoesNotExist:
            raise serializers.ValidationError(
                _("Invalid phone number or password."), code='authorization')

        if not teacher.check_password(password):
            raise serializers.ValidationError(
                _("Invalid phone number or password."), code='authorization')

        if not teacher.is_active:
            raise serializers.ValidationError(
                _("Your account has been deactivate."), code='inactive')

        attrs['teacher'] = teacher
        return attrs


class ChangeTeacherPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True, trim_whitespace=False)
    new_password1 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True, trim_whitespace=False)
    new_password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        teacher = self.context.get('teacher')
        old_password = attrs.get('old_password')

        if not teacher.check_password(old_password):
            msg = {'old_password': _("Wrong old password.")}
            raise serializers.ValidationError(msg)

        if attrs['new_password1'] != attrs['new_password2']:
            error_message = {"new_password2": _(
                "The two new passwords do not match.")}
            raise serializers.ValidationError(error_message)

        # Validate new password strength using Django's built-in validators
        new_password = attrs['new_password1']
        try:
            validate_password(new_password, teacher)
        except ValidationError as e:
            raise serializers.ValidationError(
                {'new_password1': list(e.messages)})

        return attrs
