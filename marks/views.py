from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from knox.auth import TokenAuthentication
from classes.models import SchoolClass
from teachers.permissions import IsTeacher
from teachers.models import Teacher
from students.models import Student
from subjects.models import Subject
from sequences.models import Sequence
from .evaluate_grade_and_remark import evaluate_grade_and_remark
from .serializers import (
    GetMarkSerializer,
    CreateOrUpdateMarkSerializer
)
from .models import Mark


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_marks_for_student(request, student_id):
    try:
        student = Student.objects.get(student_id=student_id)
    except Student.DoesNotExist:
        msg = ['Student not found']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    marks = student.mark_set.all()
    serializer = GetMarkSerializer(marks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsTeacher])
def create_or_update_mark(request, class_id, subject_id):
    try:
        subject = Subject.objects.get(pk=subject_id)
    except Subject.DoesNotExist:
        msg = ['Subject not found']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    try:
        school_class = SchoolClass.objects.get(pk=class_id)
    except SchoolClass.DoesNotExist:
        msg = ['Class not found']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if not school_class.periods.filter(subject=subject).exists():
        msg = ['The subject is not taught in this class']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if not school_class.year.is_active:
        msg = ['You can only fill marks for subjects in the active year.']
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    try:
        sequence = Sequence.objects.get(is_active=True)
    except Sequence.DoesNotExist:
        msg = ['There is no active sequence at this moment. Please contact the admin.']
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    if not sequence.term.year.is_active:
        msg = ['You can only submit marks for an active year.']
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    try:
        teacher = Teacher.objects.get(pk=request.user.pk)
    except Teacher.DoesNotExist:
        msg = ['You are not authorized to take that action.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    periods = school_class.periods.filter(teacher=teacher, subject=subject)
    if not periods.exists():
        msg = ['You are not assigned to this subject in this class']
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    serializer = CreateOrUpdateMarkSerializer(data=request.data)

    if serializer.is_valid():
        class_list = serializer.validated_data['class_list']
        competency = serializer.validated_data.get('competency', None)

        for student_info in class_list:
            student_id = student_info['student_id']
            subject_score = student_info['score']

            if subject_score == '':
                mark = Mark.objects.filter(
                    student__student_id=student_id, subject=subject, sequence=sequence)
                if mark.exists():
                    mark.last().delete()

                continue

            try:
                float(subject_score)
            except (ValueError, TypeError):
                msg = [f'"{subject_score}" is not a valid score...']
                return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

            if float(subject_score) < 0 or float(subject_score) > 20:
                msg = [
                    f'{subject_score} is not a valid score. Mark range (0 to 20)']
                return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

            try:
                student = Student.objects.get(student_id=student_id)
            except Student.DoesNotExist:
                msg = ['Student not found']
                return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

            grade, remark = evaluate_grade_and_remark(
                score=float(subject_score))

            try:
                '''Update happens here'''
                mark = Mark.objects.get(
                    student=student, subject=subject, sequence=sequence)
                mark.score = round(float(subject_score), 3)
                mark.grade = grade
                mark.remark = remark
                mark.teacher = teacher
                mark.competency = competency
                mark.save()

            except Mark.DoesNotExist:
                '''Creation occurs here'''
                Mark.objects.create(
                    subject=subject,
                    student=student,
                    sequence=sequence,
                    teacher=teacher,
                    score=round(float(subject_score), 3),
                    grade=grade,
                    remark=remark,
                    competency=competency
                )

        return Response(status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['GET'])
@permission_classes([IsAuthenticated, IsTeacher])
@authentication_classes([TokenAuthentication])
def get_student_list_in_class_for_marks_input(request, class_id, subject_id):
    try:
        school_class = SchoolClass.objects.get(pk=class_id)
    except SchoolClass.DoesNotExist:
        msg = ['The class you want to get students for was not found.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        msg = ['Subject not found']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if not school_class.periods.filter(subject=subject).exists():
        msg = ['The subject is not taught in this class']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    try:
        sequence = Sequence.objects.get(is_active=True)
    except Sequence.DoesNotExist:
        msg = ['There is no active sequence at this moment. Please contact the admin.']
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    if not sequence.term.is_active:
        msg = ['You can only submit marks for an active term.']
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    if not sequence.term.year.is_active:
        msg = ['You can only submit marks for an active year.']
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    students = school_class.student_set.all()

    response_data = []
    for student in students:
        mark = Mark.objects.filter(
            student=student, subject=subject, sequence=sequence)
        if mark:
            score = mark[0].score
            competency = mark[0].competency if mark[0].competency else ""
        else:
            score = ""
            competency = ""

        data = {
            'name': student.name,
            'image': student.get_image_url(),
            'student_id': student.student_id,
            'gender': student.gender,
            'score': score,
            'competency': competency
        }

        response_data.append(data)

    return Response(response_data, status=status.HTTP_200_OK)
