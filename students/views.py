# from django.db.models import Sum, F, FloatField, ExpressionWrapper
from django.utils.text import slugify
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)
from cloudinary import api as cloudinary_api
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from knox.auth import TokenAuthentication
from accounts.permissions import IsAdminUser, IsSuperuser
from classes.models import SchoolClass
from classes.serializers import GetSchoolClassSerializer
from years.models import Year
from sequences.models import Sequence
from .models import Student
from .student_id import StudentIDGenerator
from .serializers import (
    CreateStudentSerializer,
    GetStudentSerializer,
    ChangeStudentImageSerializer
)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_all_students_in_class(request, class_id):
    try:
        school_class = SchoolClass.objects.get(pk=class_id)
    except SchoolClass.DoesNotExist:
        msg = ['Class not found.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetStudentSerializer(
        school_class.student_set.all(), many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def create_student(request, class_id):
    # For super administrator only
    try:
        student_class = SchoolClass.objects.get(pk=class_id)
    except SchoolClass.DoesNotExist:
        msg = ["Class not found. You can't assign a student to an unknown class."]
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if not student_class.year.is_active:
        msg = [
            "You can only assign students to a class in the current active academic year."]
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    serializer = CreateStudentSerializer(data=request.data)

    if serializer.is_valid():
        name = serializer.validated_data['name']

        if Student.objects.filter(name=name, student_class=student_class).exists():
            msg = [
                f"A student with the name {name} already exists in this class."]
            return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

        else:
            school_initials = "FAS"  # Change with actual school initials or save in db
            query = Student.objects.all().values_list('student_id', flat=True)
            student_id_gen = StudentIDGenerator(school_initials, query=query)
            student_id = student_id_gen.generate_student_id()

            if student_id == "Ids are exhausted":
                msg = [
                    "Ids are exhausted. Please contact the developer (EGBE Victor Junior)."]
                return Response({'error': msg}, status=status.HTTP_507_INSUFFICIENT_STORAGE)

            student = Student(**serializer.validated_data)
            student.student_class = student_class
            student.student_id = student_id
            student.slug = slugify(f'{student_id}-{student.name}')
            student.save()
            data = GetStudentSerializer(student).data
            return Response(data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_student(request, student_id):
    # For administrators only
    try:
        student = Student.objects.get(student_id=student_id)
    except Student.DoesNotExist:
        msg = ['Student not found']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    # Calculate averages
    sequences = Sequence.objects.all()
    averages = []
    for sequence in sequences:
        total_score = 0
        total_coefficient = 0
        marks = student.marks.filter(sequence=sequence)
        for mark in marks:
            score_coefficient = mark.score * mark.subject.coefficient
            total_score += score_coefficient
            total_coefficient += mark.subject.coefficient

        average = total_score / total_coefficient if total_coefficient > 0 else 0
        averages.append({'name': sequence.short_name,
                        'average': round(average, 2)})

    if len(averages) == 1:
        if averages[0]['average'] == 0:
            averages = []

    # Student absences
    absences_count = student.absences.all().filter(sequence__is_active=True).count()

    class_mates = student.student_class.student_set.all()
    serializer = GetStudentSerializer(student)
    class_mates_serializer = GetStudentSerializer(class_mates, many=True)
    response_data = {
        'student': serializer.data,
        'class_mates': class_mates_serializer.data,
        'performance': averages,
        'absences': absences_count,
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_all_students_in_school(request):
    '''Returns students of the current active year'''
    students = Student.objects.filter(
        student_class__year__is_active=True).order_by('-pk')
    serializer = GetStudentSerializer(students, many=True)
    data = {
        'count': students.count(),
        'students': serializer.data
    }

    return Response(data, status=status.HTTP_200_OK)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_all_students_in_given_year(request, year_id):
    '''Returns students of the given year'''
    try:
        Year.objects.get(id=year_id)
    except Year.DoesNotExist:
        msg = ['Year not found']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    students = Student.objects.filter(student_class__year_id=year_id)
    serializer = GetStudentSerializer(students, many=True)
    data = {
        'count': students.count(),
        'students': serializer.data
    }

    return Response(data, status=status.HTTP_200_OK)


@api_view(http_method_names=['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def delete_student(request, student_id):
    # For super administrator only
    try:
        student = Student.objects.get(student_id=student_id)
    except Student.DoesNotExist:
        msg = ['Student not found']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if not student.student_class.year.is_active:
        msg = ['You can only delete students from the current academic year']
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    student.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(http_method_names=['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def update_student(request, student_id, class_id):
    # For super administrator only
    try:
        student = Student.objects.get(student_id=student_id)
    except Student.DoesNotExist:
        msg = ['Student not found']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    try:
        student_class = SchoolClass.objects.get(pk=class_id)
    except SchoolClass.DoesNotExist:
        msg = ['Class not found']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if not student_class.year.is_active:
        msg = ['You can only edit students in the current academic year.']
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    serializer = CreateStudentSerializer(student, data=request.data)
    if serializer.is_valid():
        serializer.save(student_class=student_class)

        # Setting new student slug
        updated_student = Student.objects.get(student_id=student_id)
        updated_student.slug = slugify(
            f'{updated_student.student_id}-{updated_student.name}')
        updated_student.save()

        response_serializer = GetStudentSerializer(updated_student)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def change_student_image(request, student_id):
    try:
        student = Student.objects.get(student_id=student_id)
    except Student.DoesNotExist:
        msg = ['Student not found']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    serializer = ChangeStudentImageSerializer(data=request.data)
    if serializer.is_valid():
        old_image = student.image
        student.image = serializer.validated_data['image']
        student.save()

        if old_image:
            # Delete old picture from server if exists
            cloudinary_api.delete_resources(
                [old_image.name],
                resource_type="image",
                type="upload"
            )

        success_message = {'image_url': student.get_image_url()}
        return Response(success_message, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_student_for_update(request, student_id):
    try:
        student = Student.objects.get(student_id=student_id)
    except Student.DoesNotExist:
        msg = ['Student not found']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    school_classes = SchoolClass.objects.all()
    school_class_serializer = GetSchoolClassSerializer(
        school_classes, many=True)
    serializer = GetStudentSerializer(student)
    new_data = serializer.data
    new_data["student_class"] = student.student_class.pk
    response_data = {
        'student': new_data,
        'classes': school_class_serializer.data
    }
    return Response(response_data, status=status.HTTP_200_OK)
