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
from sequences.models import Sequence
from students.models import Student
from teachers.models import Teacher
from terms.models import Term
from years.models import Year
from .models import StudentAbsence, TeacherAbsence
from .serializers import CreateOrUpdateAbsentSerializer, TeacherCreateOrUpdateAbsentSerializer


@api_view(http_method_names=('POST', ))
@authentication_classes((TokenAuthentication, ))
@permission_classes((IsAuthenticated, IsSuperuser))
def create_or_update_students_absences(request):
    try:
        sequence = Sequence.objects.get(is_active=True)
    except Sequence.DoesNotExist:
        msg = 'There is no active sequence. Please create one.'
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if not sequence.term.is_active:
        msg = f'You can only create absences in an active term.'
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    if not sequence.term.year.is_active:
        msg = f'You can only create absences in an active year.'
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    serializer = CreateOrUpdateAbsentSerializer(data=request.data)

    if serializer.is_valid():

        date = serializer.validated_data['date']
        class_list = serializer.validated_data['class_list']

        for student_info in class_list:
            student_id = student_info['student_id']
            is_absent = student_info['is_absent'] == "true"
            not_absent = student_info['is_absent'] == "false"

            try:
                student = Student.objects.get(student_id=student_id)
            except Student.DoesNotExist:
                msg = 'Student not found'
                return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

            try:
                '''Updating occurs here'''
                absence = StudentAbsence.objects.get(
                    student=student, date=date)
                if not_absent:
                    absence.delete()

            except StudentAbsence.DoesNotExist:
                '''Creation occurs here'''
                if is_absent:
                    StudentAbsence.objects.create(
                        student=student,
                        date=date,
                        sequence=sequence
                    )
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=('GET', ))
@authentication_classes((TokenAuthentication, ))
@permission_classes((IsAuthenticated, IsAdminUser))
def get_total_sequence_absences(request, student_id, sequence_id):

    try:
        student = Student.objects.get(student_id=student_id)
    except Student.DoesNotExist:
        msg = 'Student not found'
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    try:
        sequence = Sequence.objects.get(pk=sequence_id)
    except Sequence.DoesNotExist:
        msg = 'Sequence not found'
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    absences = StudentAbsence.objects.filter(
        student=student, sequence=sequence)
    data = {
        'Student': student.name,
        'student_id': student.student_id,
        'number_of_absences': absences.count(),
        'sequence': sequence.name,
        'term': sequence.term.name,
        'year': sequence.term.year.name
    }

    return Response(data, status=status.HTTP_200_OK)


@api_view(http_method_names=('GET', ))
@authentication_classes((TokenAuthentication, ))
@permission_classes((IsAuthenticated, IsAdminUser))
def get_total_term_absences(request, student_id, term_id):

    try:
        term = Term.objects.get(pk=term_id)
    except Term.DoesNotExist:
        msg = 'Term not found'
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    try:
        student = Student.objects.get(student_id=student_id)
    except Student.DoesNotExist:
        msg = 'Student not found'
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    absences = StudentAbsence.objects.filter(
        student=student, sequence__term=term)
    data = {
        'Student': student.name,
        'student_id': student.student_id,
        'number_of_absences': absences.count(),
        'term': term.name,
        'year': term.year.name
    }

    return Response(data, status=status.HTTP_200_OK)


@api_view(http_method_names=('POST', ))
@authentication_classes((TokenAuthentication, ))
@permission_classes((IsAuthenticated, IsSuperuser))
def create_or_update_teachers_absences(request, teacher_id):
    try:
        Year.objects.get(is_active=True)
    except Year.DoesNotExist:
        msg = 'There is no active year. Please create one.'
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    try:
        teacher = Teacher.objects.get(pk=teacher_id)
    except Teacher.DoesNotExist:
        msg = 'Teacher not found.'
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    serializer = TeacherCreateOrUpdateAbsentSerializer(data=request.data)

    if serializer.is_valid():

        date = serializer.validated_data['date']
        is_absent = serializer.validated_data['is_absent']

        try:
            '''Updating occurs here'''
            absence = TeacherAbsence.objects.get(teacher=teacher, date=date)
            if not is_absent:
                absence.delete()

        except TeacherAbsence.DoesNotExist:
            '''Creation occurs here'''
            if is_absent:
                TeacherAbsence.objects.create(teacher=teacher, date=date)
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
