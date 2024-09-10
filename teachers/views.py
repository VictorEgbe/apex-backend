from operator import itemgetter

from django.contrib.auth import login as django_login
from django.db.models import Sum, Value
from django.utils.text import slugify
from django.db.models.functions import Coalesce
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from cloudinary import api as cloudinary_api
from knox.auth import TokenAuthentication
from knox.views import (
    LogoutView as KnoxLogoutView,
    LogoutAllView as KnoxLogoutAllView
)
from accounts.permissions import IsAdminUser, IsSuperuser
from departments.models import Department
from subjects.serializers import GetTeacherPeriodSerializer
from knox.models import AuthToken
from .serializers import (
    CreateTeacherSerializer,
    GetTeacherSerializer,
    UpdateTeacherSerializer,
    ChangeTeacherImageSerializer,
    ChangeTeacherPasswordBySuperUserSerializer,
    LoginTeacherSerializer,
    ChangeTeacherPasswordSerializer
)
from .models import Teacher
from .permissions import IsTeacher
from subjects.utils import get_ordered_periods


@api_view(http_method_names=['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def create_teacher(request, department_id):
    # Only for the super administrator

    try:
        department = Department.objects.get(pk=department_id)
    except Department.DoesNotExist:
        msg = ['Department not found']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    serializer = CreateTeacherSerializer(data=request.data)

    if serializer.is_valid():
        name = serializer.validated_data.get('name')

        if Teacher.objects.filter(name=name, department=department).exists():
            msg = [
                f"A teacher with the name {name} already exists in {department.name} department"]
            return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

        teacher = serializer.save(department=department)
        teacher.slug = slugify(f'{teacher.pk}-{teacher.name}')
        teacher.save()
        data = GetTeacherSerializer(teacher).data
        return Response(data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['POST'])
@authentication_classes((TokenAuthentication, ))
@permission_classes((AllowAny, ))
def login_teacher(request):
    # Login for teacher frontend app

    serializer = LoginTeacherSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    teacher = serializer.validated_data['teacher']
    django_login(request=request, user=teacher)
    instance, token = AuthToken.objects.create(user=teacher)
    response_data = {
        'teacher': GetTeacherSerializer(teacher, many=False).data,
        'auth': {
            'token': token,
            'expiry': instance.expiry
        }
    }
    return Response(response_data, status=status.HTTP_202_ACCEPTED)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_all_teachers(request):
    # For administrators only
    teachers = Teacher.objects.all()
    serializer = GetTeacherSerializer(teachers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_teacher(request, teacher_id):
    # For administrators only
    try:
        teacher = Teacher.objects.get(pk=teacher_id)
    except Teacher.DoesNotExist:
        msg = ['Teacher not found.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    absences_count = teacher.absences.count()

    teacher_periods = get_ordered_periods(teacher.pk)
    serializer = GetTeacherSerializer(teacher)
    department_teachers = teacher.department.teachers.all()

    response_data = {
        'teacher': serializer.data,
        'department_teachers': GetTeacherSerializer(department_teachers, many=True).data,
        'absences': absences_count,
        "periods": GetTeacherPeriodSerializer(teacher_periods, many=True).data,
        **teacher.periods.aggregate(total=Coalesce(Sum('number_of_periods'), Value(0)))
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_just_teacher_info(request, teacher_id):
    # For administrators only used in getting teacher's info that can be updated
    try:
        teacher = Teacher.objects.get(pk=teacher_id)
    except Teacher.DoesNotExist:
        msg = ['Teacher not found.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetTeacherSerializer(teacher)
    data = serializer.data
    data["department"] = teacher.department.id
    return Response(data, status=status.HTTP_200_OK)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsTeacher])
def load_teacher(request):
    # For teachers only
    try:
        teacher = Teacher.objects.get(pk=request.user.id)
    except Teacher.DoesNotExist:
        msg = ['Teacher not found.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetTeacherSerializer(teacher)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def delete_teacher(request, teacher_id):
    # For superusers only
    try:
        teacher = Teacher.objects.get(pk=teacher_id)
    except Teacher.DoesNotExist:
        msg = ['Teacher not found.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)
    image = teacher.image
    teacher.delete()
    if image:
        cloudinary_api.delete_resources(
            [image.name],
            resource_type="image",
            type="upload"
        )

    success_message = {'message': _('Teacher deleted successfully.')}
    return Response(success_message, status=status.HTTP_200_OK)


@api_view(http_method_names=['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ])
def update_teacher(request, teacher_id, new_department_id):
    # Super administrator only
    try:
        teacher = Teacher.objects.get(pk=teacher_id)
    except Teacher.DoesNotExist:
        msg = ['Teacher not found.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if not (request.user.is_superuser or request.user.id == teacher.id):
        error_message = {'error': [_(
            'You are not authorized to take that action.')]}
        return Response(error_message, status=status.HTTP_403_FORBIDDEN)

    try:
        new_department = Department.objects.get(pk=new_department_id)
    except Department.DoesNotExist:
        msg = ['Department not found']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    serializer = UpdateTeacherSerializer(teacher, data=request.data)

    if serializer.is_valid():
        serializer.save(department=new_department)

        # Update the slug
        updated_teacher = Teacher.objects.get(pk=teacher_id)
        updated_teacher.slug = slugify(f'{teacher.pk}-{teacher.name}')
        updated_teacher.save()

        data = GetTeacherSerializer(updated_teacher).data
        return Response(data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ])
def teacher_password_change(request, teacher_id):
    # For teachers and super administrator only
    try:
        teacher = Teacher.objects.get(pk=teacher_id)
    except Teacher.DoesNotExist:
        msg = ['Teacher not found.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if not (request.user.is_superuser or request.user.id == teacher.id):
        error_message = {'error': [_(
            'You are not authorized to take that action.')]}
        return Response(error_message, status=status.HTTP_403_FORBIDDEN)

    if request.user.is_superuser:
        serializer = ChangeTeacherPasswordBySuperUserSerializer(
            data=request.data)
    elif request.user.id == teacher.id:
        serializer = ChangeTeacherPasswordSerializer(
            data=request.data, context={'teacher': teacher})

    if serializer.is_valid():
        password = serializer.validated_data.get('new_password1')
        teacher.set_password(password)
        teacher.save()
        success_message = {'message': _("Password changed successfully.")}
        return Response(success_message, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ])
def change_teacher_image(request, teacher_id):
    # For teachers and super administrator only
    try:
        teacher = Teacher.objects.get(pk=teacher_id)
    except Teacher.DoesNotExist:
        error_message = {'error': [_('Teacher does not exist.')]}
        return Response(error_message, status=status.HTTP_404_NOT_FOUND)

    # Check if the requesting user is allowed to update the teacher's image
    if not (request.user.is_superuser or request.user.id == teacher.id):
        error_message = {'error': [_(
            'You are not authorized to take that action.')]}
        return Response(error_message, status=status.HTTP_403_FORBIDDEN)

    else:
        serializer = ChangeTeacherImageSerializer(data=request.data)
        if serializer.is_valid():
            old_image = teacher.image
            teacher.image = serializer.validated_data['image']
            teacher.save()

            if old_image:
                # Delete old picture from server if exists
                cloudinary_api.delete_resources(
                    [old_image.name],
                    resource_type="image",
                    type="upload"
                )
            if request.user.id == teacher.id:
                success_message = GetTeacherSerializer(teacher).data
            else:
                success_message = {'image_url': teacher.get_image_url}

            return Response(success_message, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsTeacher])
def get_teacher_classes(request, teacher_id):
    try:
        teacher = Teacher.objects.get(pk=teacher_id)
    except Teacher.DoesNotExist:
        error_message = {'error': [_('Teacher does not exist.')]}
        return Response(error_message, status=status.HTTP_404_NOT_FOUND)

    periods = teacher.periods.all()

    if not periods.exists():
        error = [_(f"{teacher.name} hasn't been assigned a class yet")]
        return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)

    classes = []
    for period in periods:
        school_class = period.school_class
        classes.append({
            'id': school_class.id,
            'name': school_class.name,
        })

     # Remove duplicate classes
    unique_classes = [dict(c) for c in {tuple(d.items()) for d in classes}]

    # Sort classes using id
    response_data = sorted(unique_classes, key=itemgetter('id'))
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsTeacher])
def get_teacher_subjects_in_a_class(request, teacher_id, class_id):
    try:
        teacher = Teacher.objects.get(pk=teacher_id)
    except Teacher.DoesNotExist:
        error_message = {'error': [_('Teacher does not exist.')]}
        return Response(error_message, status=status.HTTP_404_NOT_FOUND)

    periods = teacher.periods.filter(school_class__id=class_id)

    if not periods.exists():
        error = [_(f"{teacher.name} doesn't teach the class")]
        return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)

    subjects = []
    for period in periods:
        subject = period.subject
        subjects.append({
            'id': subject.id,
            'name': subject.name,
            'short_name': subject.short_name
        })

    unique_subjects = [dict(s) for s in {tuple(d.items()) for d in subjects}]

    return Response(unique_subjects, status=status.HTTP_200_OK)


class LogoutTeacher(KnoxLogoutView):
    # Logout from currently used device
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class LogoutTeacherAll(KnoxLogoutAllView):
    # Logout from all devices
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
