from django.contrib.auth import login as django_login
from django.utils.translation import gettext as _
from django.utils.text import slugify

from cloudinary import api as cloudinary_api

from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny
)

from knox.auth import TokenAuthentication
from knox.models import AuthToken
from knox.views import (
    LogoutView as KnoxLogoutView,
    LogoutAllView as KnoxLogoutAllView
)

from .models import User
from .permissions import IsAdminUser, IsSuperuser
from .serializers import (
    ChangeAdminImageSerializer,
    ChangeAdminPasswordSerializer,
    ChangeAdminPasswordSerializerBySuperUser,
    CreateAdminUserSerializer,
    GetAdminUserSerializer,
    LoginAdminSerializer,
    UpdateAdminSerializer
)


@api_view(http_method_names=['POST'])
@authentication_classes((TokenAuthentication, ))
@permission_classes((IsAuthenticated, IsSuperuser))
def create_admin_user(request):
    serializer = CreateAdminUserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.slug = slugify(f'{user.pk}-{user.name}')
        user.save()
        response_data = GetAdminUserSerializer(user, many=False).data
        return Response(response_data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['POST'])
@authentication_classes((TokenAuthentication, ))
@permission_classes((AllowAny, ))
def login_admin_user(request):
    serializer = LoginAdminSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    django_login(request=request, user=user)
    instance, token = AuthToken.objects.create(user=user)
    response_data = {
        'user': GetAdminUserSerializer(user, many=False).data,
        'auth': {
            'token': token,
            'expiry': instance.expiry
        }
    }
    return Response(response_data, status=status.HTTP_202_ACCEPTED)


@api_view(http_method_names=['GET'])
@authentication_classes((TokenAuthentication, ))
@permission_classes((IsAuthenticated, IsAdminUser))
def get_admin_user(request, admin_id):
    try:
        user = User.objects.get(id=admin_id, is_admin=True)
    except User.DoesNotExist:
        error_message = {
            'error': [_('Admin not found')]
        }
        return Response(error_message, status=status.HTTP_404_NOT_FOUND)

    others = User.objects.filter(is_admin=True)
    others_serializer = GetAdminUserSerializer(others, many=True)
    serializer = GetAdminUserSerializer(user, many=False)

    response_data = {
        'admin': serializer.data,
        'others': others_serializer.data
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(http_method_names=['GET'])
@authentication_classes((TokenAuthentication, ))
@permission_classes((IsAuthenticated, IsAdminUser))
def get_all_admin_users(request):
    admin_users = User.objects.filter(is_admin=True).order_by('-pk')
    serializer = GetAdminUserSerializer(admin_users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['PUT'])
@authentication_classes((TokenAuthentication, ))
@permission_classes((IsAuthenticated, IsAdminUser))
def change_admin_password(request, admin_id):
    try:
        admin = User.objects.get(pk=admin_id, is_admin=True)
    except User.DoesNotExist:
        error_message = {'error': [_('Admin not found')]}
        return Response(error_message, status=status.HTTP_404_NOT_FOUND)

    # Check if the requesting user is allowed to change the password
    if not (request.user.is_superuser or request.user.id == admin.id):
        error_message = {'error': [_(
            'You are not authorized to take that action.')]}
        return Response(error_message, status=status.HTTP_403_FORBIDDEN)

    else:

        if request.user.is_superuser:
            serializer = ChangeAdminPasswordSerializerBySuperUser(
                data=request.data, context={'user': admin}
            )
        elif request.user.id == admin.id:
            serializer = ChangeAdminPasswordSerializer(
                data=request.data, context={'user': admin})

        if serializer.is_valid():
            admin.set_password(serializer.validated_data['new_password1'])
            admin.save()
            success_message = {'message': _(
                "Admin's password changed successfully.")}
            return Response(success_message, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def update_admin(request, admin_id):
    try:
        admin = User.objects.get(pk=admin_id, is_admin=True)
    except User.DoesNotExist:
        error_message = {'error': [_('Admin not found')]}
        return Response(error_message, status=status.HTTP_404_NOT_FOUND)

    # Check if the requesting user is allowed to update the admin's info
    if not (request.user.is_superuser or request.user.id == admin.id):
        error_message = {'error': [_(
            'You are not authorized to take that action.')]}
        return Response(error_message, status=status.HTTP_403_FORBIDDEN)

    else:
        serializer = UpdateAdminSerializer(admin, data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.slug = slugify(f'{user.pk}-{user.name}')
            user.save()
            response_data = GetAdminUserSerializer(user).data
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def delete_admin(request, admin_id):
    try:
        admin = User.objects.get(pk=admin_id)
    except User.DoesNotExist:
        error_message = {'error': [_('Admin not found')]}
        return Response(error_message, status=status.HTTP_404_NOT_FOUND)

    # Ensure that only superusers can delete admin accounts
    if not request.user.is_superuser:
        error_message = {
            'error': [_('You are not authorized to take that action.')]}
        return Response(error_message, status=status.HTTP_403_FORBIDDEN)

    else:
        admin.delete()
        success_message = {'message': [_('Admin deleted successfully.')]}
        return Response(success_message, status=status.HTTP_204_NO_CONTENT)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def load_admin(request):
    response_data = GetAdminUserSerializer(request.user).data
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(http_method_names=['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def change_admin_image(request, admin_id):
    try:
        admin = User.objects.get(pk=admin_id, is_admin=True)
    except User.DoesNotExist:
        error_message = {'error': [_('Admin not found')]}
        return Response(error_message, status=status.HTTP_404_NOT_FOUND)

    # Check if the requesting user is allowed to update the admin's info
    if not (request.user.is_superuser or request.user.id == admin.id):
        error_message = {'error': [_(
            'You are not authorized to take that action.')]}
        return Response(error_message, status=status.HTTP_403_FORBIDDEN)

    else:
        serializer = ChangeAdminImageSerializer(data=request.data)
        if serializer.is_valid():
            old_image = admin.image
            admin.image = serializer.validated_data['image']
            admin.save()

            if old_image:
                # Delete old picture from server if exists
                cloudinary_api.delete_resources(
                    [old_image.name],
                    resource_type="image",
                    type="upload"
                )

            return Response(GetAdminUserSerializer(admin).data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_just_admin_info(request, admin_id):
    try:
        admin = User.objects.get(pk=admin_id)
    except User.DoesNotExist:
        msg = ['Admin not found.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetAdminUserSerializer(admin, many=False)
    data = serializer.data
    data.pop("image")
    data.pop("created_at")
    data.pop("is_admin")
    data.pop("age")
    data.pop("last_login")
    data.pop("slug")
    data.pop("id")
    return Response(data, status=status.HTTP_200_OK)


class LogoutAdmin(KnoxLogoutView):
    # Logout from currently used device
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class LogoutAllAdmin(KnoxLogoutAllView):
    # Logout from all devices
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
