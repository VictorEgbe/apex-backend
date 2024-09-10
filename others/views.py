from django.db.models import Count, Q, Avg
from django.utils.translation import gettext as _

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from knox.auth import TokenAuthentication

from absences.models import TeacherAbsence, StudentAbsence
from accounts.permissions import IsAdminUser
from accounts.serializers import GetAdminUserSerializer
from accounts.models import User
from classes.models import SchoolClass
from marks.models import Mark
from sequences.models import Sequence
from students.models import Student
from subjects.models import Subject
from teachers.models import Teacher
from teachers.serializers import GetTeacherSerializer
from years.models import Year

from students.serializers import GetStudentSerializer


@api_view(http_method_names=["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def dashboard(request):
    response_data = {}

    # Admins
    admins_count = User.objects.filter(is_admin=True).aggregate(
        total=Count('id'),
        males=Count('id', filter=Q(gender='Male')),
        females=Count('id', filter=Q(gender='Female'))
    )

    try:
        current_active_year = Year.objects.get(is_active=True)
    except Year.DoesNotExist:
        response_data["students"] = {'total': 0, 'gender': [
            {'name': "Students", "male": 0, "female": 0}]}
        response_data["admins"] = {'total': admins_count['total'], 'gender': [
            {'name': "Admins", 'male': admins_count['males'], 'female': admins_count['females']}]}
        response_data["teachers"] = {'total': 0, 'gender': [
            {'name': "Teachers", "male": 0, "female": 0}]}
        response_data["absences"] = [
            {'name': 'Teachers', 'value': 0},
            {'name': 'Students', 'value': 0},
        ]
        response_data["last_five_students_registered"] = []
        response_data["classes"] = []
        return Response(response_data, status=status.HTTP_200_OK)

    # Students of current active year
    students_count = Student.objects.filter(
        student_class__year_id=current_active_year.id).aggregate(
        total=Count('id'),
        males=Count('id', filter=Q(gender='Male')),
        females=Count('id', filter=Q(gender='Female'))
    )

    # Teachers
    teachers_count = Teacher.objects.all().aggregate(
        total=Count('id'),
        males=Count('id', filter=Q(gender='Male')),
        females=Count('id', filter=Q(gender='Female'))
    )

    # Absences
    teacher_absences = TeacherAbsence.objects.filter(
        period__school_class__year=current_active_year
    ).aggregate(total=Count('id'))
    student_absences = StudentAbsence.objects.filter(
        student__student_class__year_id=current_active_year.id).aggregate(total=Count('id'))
    absences_count = [
        {'name': 'Teachers', 'value': teacher_absences['total']},
        {'name': 'Students', 'value': student_absences['total']}
    ]

    # Last Five registered students
    last_five_students = Student.objects.filter(
        student_class__year_id=current_active_year.id).order_by('-id')[:5]
    serializer = GetStudentSerializer(last_five_students, many=True)

    # Classes(of active year) and total students count and male and female students count
    classes_data = SchoolClass.objects.filter(year_id=current_active_year.id).annotate(
        total=Count('student'),
        males=Count('student', filter=Q(student__gender='Male')),
        females=Count('student', filter=Q(student__gender='Female')),
    ).values('id', 'short_name', 'males', 'females', 'total')

    # Response Data
    response_data["students"] = {'total': students_count['total'], 'gender': [
        {'name': "Students", 'male': students_count['males'], 'female': students_count['females']}]}

    response_data["admins"] = {'total': admins_count['total'], 'gender': [
        {'name': "Admins", 'male': admins_count['males'], 'female': admins_count['females']}]}

    response_data["teachers"] = {'total': teachers_count['total'], 'gender': [
        {'name': "Teachers", 'male': teachers_count['males'], 'female': teachers_count['females']}]}

    response_data["absences"] = absences_count
    response_data["last_five_students_registered"] = serializer.data
    response_data["classes"] = list(classes_data)

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(http_method_names=["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_class_statistics_for_a_subject(request, class_id, subject_id, sequence_id):
    # Get the sequence
    try:
        sequence_obj = Sequence.objects.get(id=sequence_id)
    except Sequence.DoesNotExist:
        error = ["Sequence not found"]
        return Response({"error": error}, status=status.HTTP_404_NOT_FOUND)

    # Get the class
    try:
        class_obj = SchoolClass.objects.get(id=class_id)
    except SchoolClass.DoesNotExist:
        error = ["Class not found"]
        return Response({"error": error}, status=status.HTTP_404_NOT_FOUND)

    # Get the subject
    try:
        subject_obj = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        error = ["Subject not found"]
        return Response({"error": error}, status=status.HTTP_404_NOT_FOUND)

    # Check to see if the subject is offered in the said class
    if not class_obj.periods.filter(subject=subject_obj).exists():
        msg = ['The subject is not taught in this class']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    # Get Marks for students that offer the subject in that class for the given sequence
    marks = Mark.objects.filter(
        student__student_class=class_obj,
        subject=subject_obj,
        sequence=sequence_obj
    )

    # Get total students that offer the subject i.e those with the marks
    total_students = marks.values_list('student', flat=True).distinct().count()
    # Get total male students
    total_male_students = marks.filter(
        student__gender='Male').distinct().count()
    # Get total female students
    total_female_students = marks.filter(
        student__gender='Female').distinct().count()

    # PASS AND PERCENTAGE PASS
    pass_score = 10
    # Get total students that had a score gte the pass_score
    pass_students = marks.filter(score__gte=pass_score).distinct().count()
    # Get the male students who passed
    male_pass_students = marks.filter(
        score__gte=pass_score, student__gender='Male').distinct().count()
    # Get the female student who passed
    female_pass_students = marks.filter(
        score__gte=pass_score, student__gender='Female').distinct().count()

    # Calculate the pass percentage
    pass_percentage = round((pass_students / total_students)
                            * 100, 2) if total_students > 0 else None
    # Calculate the male pass percentage
    male_pass_percentage = round(
        (male_pass_students / total_male_students) * 100, 2) if total_male_students > 0 else None
    # Calculate the female pass percentage
    female_pass_percentage = round(
        (female_pass_students / total_female_students) * 100, 2) if total_female_students > 0 else None

    # FAIL AND PERCENTAGE FAIL
    # Get total students that failed
    fail_students = total_students - pass_students
    # Get the male students who failed
    male_fail_students = total_male_students - male_pass_students
    # Get the female students who failed
    female_fail_students = total_female_students - female_pass_students

    # Calculate the fail percentage
    fail_percentage = 100 - pass_percentage if total_students > 0 else None
    # Calculate the male fail percentage
    male_fail_percentage = 100 - male_pass_percentage if total_male_students > 0 else None
    # Calculate the female fail percentage
    female_fail_percentage = 100 - \
        female_pass_percentage if total_female_students > 0 else None

    # Calculate the average mark score of the class in the subject
    average_score = marks.aggregate(
        Avg('score'))['score__avg'] if marks.exists() else None

    # Get best three students, ordering in descending order
    best_three_students = [
        {'id': m.student.pk,
            'name': m.student.name,
            'score': m.score,
            'gender': m.student.gender,
            'student_id': m.student.student_id,
            'image': m.student.get_image_url()
         } for m in marks.order_by('-score')[:3]
    ]
    # Get last three students, ordering in descending order
    last_three_students = sorted([
        {
            'id': m.student.pk,
            'name': m.student.name,
            'score': m.score,
            'gender': m.student.gender,
            'student_id': m.student.student_id,
            'image': m.student.get_image_url()
        } for m in marks.order_by('score')[:3]
    ], key=lambda obj: obj['score'], reverse=True)

    # Response data
    response_data = {
        'subject': subject_obj.short_name,
        'class_obj': class_obj.name,
        'sequence': sequence_obj.short_name,
        'enrolment': {
            'total_students': total_students,
            'total_male_students': total_male_students,
            'total_female_students': total_female_students,
        },
        'passes': {
            'pass_students': pass_students,
            'male_pass_students': male_pass_students,
            'female_pass_students': female_pass_students,
        },
        'pass_percentages': {
            'pass_percentage': pass_percentage,
            'male_pass_percentage': male_pass_percentage,
            'female_pass_percentage': female_pass_percentage,
        },
        'fails': {
            'fail_students': fail_students,
            'male_fail_students': male_fail_students,
            'female_fail_students': female_fail_students,
        },
        'fail_percentages': {
            'fail_percentage': fail_percentage,
            'male_fail_percentage': male_fail_percentage,
            'female_fail_percentage': female_fail_percentage,
        },
        'average_score': round(float(average_score.to_eng_string()), 2) if average_score else None,
        'best_three_students': best_three_students,
        'last_three_students': last_three_students
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(http_method_names=['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
@authentication_classes([TokenAuthentication])
def search(request):
    search = request.GET.get('query', None)
    results = []

    if search:
        students = Student.objects.filter(
            name__icontains=search) | Student.objects.filter(student_id__icontains=search)
        teachers = Teacher.objects.filter(
            name__icontains=search) | Teacher.objects.filter(phone__icontains=search)
        admins = User.objects.filter(is_admin=True, name__icontains=search) | User.objects.filter(
            is_admin=True, phone__icontains=search)

        students_data = GetStudentSerializer(students, many=True).data
        teachers_data = GetTeacherSerializer(teachers, many=True).data
        admins_data = GetAdminUserSerializer(admins, many=True).data

        results = list(students_data) + list(teachers_data) + list(admins_data)

    return Response(results, status=status.HTTP_200_OK)
