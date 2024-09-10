from django.utils.text import slugify

from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from knox.auth import TokenAuthentication
from accounts.permissions import IsAdminUser, IsSuperuser
from .models import Department
from .serializers import (
    CreateDepartmentSerializer,
    GetDepartmentSerializer,
    AllDepartmentsSerializer
)


@api_view(http_method_names=['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def create_department(request):
    serializer = CreateDepartmentSerializer(data=request.data)
    if serializer.is_valid():
        department = serializer.save()
        department.slug = slugify(f'{department.id}-{department.name}')
        department.save()
        data = GetDepartmentSerializer(department).data
        return Response(data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_department(request, department_id):
    try:
        department = Department.objects.get(pk=department_id)
    except Department.DoesNotExist:
        msg = [f'Department not found.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetDepartmentSerializer(department)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_just_department(request, department_id):
    try:
        department = Department.objects.get(pk=department_id)
    except Department.DoesNotExist:
        msg = [f'Department not found.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    data = {
        'id': department.id,
        'name': department.name,
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_teachers_in_department(request, department_id):
    try:
        department = Department.objects.get(pk=department_id)
    except Department.DoesNotExist:
        msg = [f'Department not found.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    teachers = department.teachers.all()
    teachers_data = []
    for teacher in teachers:
        data = {
            'id': teacher.id,
            'name': teacher.name,
        }
        teachers_data.append(data)

    try:
        hod_info = department.teachers.get(pk=department.hod_id)
        hod = {
            'id': hod_info.id,
            'name': hod_info.name,
        }
    except department.teachers.model.DoesNotExist:
        hod = None

    response_data = {
        'teachers': teachers_data,
        'hod': hod,
        'name': department.name
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_all_departments(request):
    departments = Department.objects.all()
    serializer = AllDepartmentsSerializer(departments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def delete_department(request, department_id):
    try:
        department = Department.objects.get(pk=department_id)
    except Department.DoesNotExist:
        msg = f'Department not found.'
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    teachers = department.teachers.all()

    if teachers:
        for teacher in teachers:
            teacher.delete()

    department.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(http_method_names=['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def update_department(request, department_id):
    try:
        department = Department.objects.get(pk=department_id)
    except Department.DoesNotExist:
        msg = [f'Department not found.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    serializer = CreateDepartmentSerializer(department, data=request.data)

    if serializer.is_valid():
        serializer.save()
        department = Department.objects.get(pk=department_id)
        department.slug = slugify(f'{department.pk}-{department.name}')
        department.save()
        data = GetDepartmentSerializer(department).data
        return Response(data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def update_department_hod(request, department_id, teacher_id):
    try:
        department = Department.objects.get(pk=department_id)
    except Department.DoesNotExist:
        msg = [f'Department not found.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    try:
        teacher = department.teachers.get(pk=teacher_id)
    except department.teachers.model.DoesNotExist:
        error_msg = [
            f"The teacher is not a member of {department.name} department"]
        return Response({'error': error_msg}, status=status.HTTP_403_FORBIDDEN)

    old_hod_id = department.hod_id
    if old_hod_id:
        old_hod = department.teachers.get(pk=old_hod_id)
        old_hod.is_hod = False
        old_hod.save()

    department.hod_id = teacher.id
    teacher.is_hod = True
    department.save()
    teacher.save()
    data = GetDepartmentSerializer(department).data
    return Response(data, status=status.HTTP_200_OK)
