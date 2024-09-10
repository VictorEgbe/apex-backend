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
from .serializers import (
    GetSubjectSerializer,
    CreateSubjectSerializer
)
from .models import Subject
from teachers.models import Teacher


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_all_subjects(request):
    subjects = Subject.objects.all().order_by('-pk')
    serializer = GetSubjectSerializer(subjects, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def create_subject(request):
    serializer = CreateSubjectSerializer(data=request.data)
    if serializer.is_valid():
        name = serializer.validated_data['name']
        coefficient = serializer.validated_data['coefficient']
        level = serializer.validated_data.get('level')

        if Subject.objects.filter(name=name, coefficient=coefficient, level=level).exists():
            error_msg = [f'Subject {name} already exist for {level} level']
            return Response({'error': error_msg}, status=status.HTTP_403_FORBIDDEN)

        subject = serializer.save()
        subject.slug = slugify(
            f'{subject.id}-{level}-level-{name}-coef-{coefficient}')
        subject.save()
        message = 'Subject created successfully'
        return Response({'message': message}, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_single_subject(request, subject_id):
    try:
        subject = Subject.objects.get(pk=subject_id)
    except Subject.DoesNotExist:
        msg = ['Subject not Found.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSubjectSerializer(subject)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def delete_subject(request, subject_id):
    try:
        subject = Subject.objects.get(pk=subject_id)
    except Subject.DoesNotExist:
        msg = ['Subject not Found.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    subject.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(http_method_names=['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def update_subject(request, subject_id):
    try:
        subject = Subject.objects.get(pk=subject_id)
    except Subject.DoesNotExist:
        msg = ['Subject not Found.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    serializer = CreateSubjectSerializer(subject, data=request.data)
    if serializer.is_valid():

        name = serializer.validated_data['name']
        coefficient = serializer.validated_data['coefficient']
        level = serializer.validated_data.get('level')
        short_name = serializer.validated_data.get('short_name', None)

        subjects_ = Subject.objects.filter(
            name=name, coefficient=coefficient, level=level)
        if subjects_.exists():
            subject = subjects_.last()
            if subject.short_name == short_name:
                error_msg = [f'Subject {name} already exist for {level} level']
                return Response({'error': error_msg}, status=status.HTTP_403_FORBIDDEN)

        serializer.save()
        updated_subject = Subject.objects.get(pk=subject_id)
        updated_subject.slug = slugify(
            f'{updated_subject.id}-{level}-level-{name}-coef-{coefficient}')
        updated_subject.save()
        message = 'Subject updated successfully'
        return Response({'msg': message}, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def add_teacher_to_subject(request, subject_id, teacher_id):
    try:
        subject = Subject.objects.get(pk=subject_id)
    except Subject.DoesNotExist:
        msg = 'Subject not Found.'
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if not subject.school_class.year.is_active:
        msg = "You can only add a teacher to a subject in the current year"
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    try:
        teacher = Teacher.objects.get(pk=teacher_id)
    except Teacher.DoesNotExist:
        msg = 'Teacher not found.'
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if subject.teachers.filter(pk=teacher.pk).exists():
        msg = f'{teacher.name} is already a teacher of {subject.name} in {subject.school_class.name}'
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)
    else:
        subject.teachers.add(teacher)
        subject.save()
        serializer = GetSubjectSerializer(subject)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def remove_teacher_to_subject(request, subject_id, teacher_id):
    try:
        subject = Subject.objects.get(pk=subject_id)
    except Subject.DoesNotExist:
        msg = 'Subject not Found.'
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if not subject.school_class.year.is_active:
        msg = "You can only remove a teacher from a subject in the current"
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    try:
        teacher = Teacher.objects.get(pk=teacher_id)
    except Teacher.DoesNotExist:
        msg = 'Teacher not found.'
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if not subject.teachers.filter(pk=teacher.pk).exists():
        msg = f'{teacher.name} is not a teacher of {subject.name} in {subject.school_class.name}'
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)
    else:
        subject.teachers.remove(teacher)
        subject.save()
        serializer = GetSubjectSerializer(subject)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_all_subjects_by_a_teacher(request, teacher_id):
    try:
        teacher = Teacher.objects.get(pk=teacher_id)
    except Teacher.DoesNotExist:
        msg = ['Teacher not Found.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    subjects = teacher.subject_set.all()
    serializer = GetSubjectSerializer(subjects, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
