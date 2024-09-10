from django.utils.text import slugify
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from knox.auth import TokenAuthentication
from accounts.permissions import IsAdminUser, IsSuperuser
from years.models import Year
from teachers.models import Teacher
from teachers.serializers import GetTeacherSerializer
from .serializers import (
    CreateSchoolClassSerializer,
    GetSchoolClassSerializer,
    GetSimpleSchoolClassSerializer,
    UpdateSchoolClassInfoSerializer
)
from .models import SchoolClass
from students.serializers import GetStudentSerializer, Student


@api_view(http_method_names=['POST'])
@permission_classes([IsAuthenticated, IsSuperuser])
@authentication_classes([TokenAuthentication])
def create_school_class(request):
    try:
        year = Year.objects.get(is_active=True)
    except Year.DoesNotExist:
        msg = ["No active year created yet."]
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    serializer = CreateSchoolClassSerializer(data=request.data)

    if serializer.is_valid():
        name = serializer.validated_data['name']

        if SchoolClass.objects.filter(name=name, year=year).exists():
            msg = [f'{name} already exists for the year {year.name}']
            return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

        else:
            short_name = serializer.validated_data.get('short_name')
            level = serializer.validated_data.get('level')
            school_class = SchoolClass(
                name=name, year=year, short_name=short_name, level=level)
            school_class.save()
            school_class.slug = slugify(
                f'{school_class.id}-{school_class.name}-{school_class.year.name}')
            school_class.save()
            response_serializer = GetSchoolClassSerializer(school_class)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_possible_class_masters(request):
    masters = Teacher.objects.filter(is_class_master=False)
    response_data = []
    for master in masters:
        response_data.append({
            'id': master.id,
            'name': master.name,
            'image': master.get_image_url
        })

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(http_method_names=['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_school_class(request, class_id):
    try:
        school_class = SchoolClass.objects.get(pk=class_id)
    except SchoolClass.DoesNotExist:
        msg = ["Class not found."]
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    students = school_class.student_set.all()
    student_serializer = GetStudentSerializer(students, many=True)

    serializer = GetSimpleSchoolClassSerializer(school_class, many=False)

    master = GetTeacherSerializer(
        school_class.master).data if school_class.master else None

    possible_prefect = school_class.student_set.filter(is_prefect=True)
    if possible_prefect:
        prefect = GetStudentSerializer(possible_prefect.first()).data
    else:
        prefect = None

    response_data = {
        'class': serializer.data,
        'students': student_serializer.data,
        'master': master,
        'prefect': prefect
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(http_method_names=['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_school_class_for_update(request, class_id):
    try:
        school_class = SchoolClass.objects.get(pk=class_id)
    except SchoolClass.DoesNotExist:
        msg = ["Class not found."]
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    school_class = {
        'id': school_class.id,
        'name': school_class.name,
        'short_name': school_class.short_name,
        'level': school_class.level
    }
    return Response(school_class, status=status.HTTP_200_OK)


@api_view(http_method_names=['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_school_classes(request):
    try:
        current_year = Year.objects.get(is_active=True)
    except Year.DoesNotExist:
        return Response([], status=status.HTTP_200_OK)

    school_classes = SchoolClass.objects.filter(year=current_year)
    serializer = GetSchoolClassSerializer(school_classes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['DELETE'])
@permission_classes([IsAuthenticated, IsSuperuser])
@authentication_classes([TokenAuthentication])
def delete_school_class(request, class_id):
    try:
        school_class = SchoolClass.objects.get(pk=class_id)
    except SchoolClass.DoesNotExist:
        msg = ["Class not found."]
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if not school_class.year.is_active:
        msg = ["You can't delete a class for an inactive year."]
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    periods = school_class.periods.all()
    students = school_class.student_set.all()

    if periods:
        for period in periods:
            period.delete()

    if students:
        for student in students:
            student.delete()

    school_class.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(http_method_names=['PUT'])
@permission_classes([IsAuthenticated, IsSuperuser])
@authentication_classes([TokenAuthentication])
def update_school_class(request, class_id):
    try:
        school_class = SchoolClass.objects.get(pk=class_id)
    except SchoolClass.DoesNotExist:
        msg = ["Class not found."]
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if not school_class.year.is_active:
        msg = ["You can't update a class for an inactive year."]
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    try:
        year = Year.objects.get(is_active=True)
    except Year.DoesNotExist:
        msg = ["No current active year."]
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    serializer = UpdateSchoolClassInfoSerializer(data=request.data)
    if serializer.is_valid():

        name = serializer.validated_data['name']
        short_name = serializer.validated_data['short_name']
        level = serializer.validated_data['level']

        current_class = SchoolClass.objects.filter(name=name, year=year)

        if current_class.exists():
            class_ = current_class.last()
            if (class_.short_name == short_name) and (class_.level == level):
                msg = [f'{name} already exists for the year {year.name}']
                return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

        school_class.name = name
        school_class.short_name = short_name
        school_class.level = level
        school_class.save()
        response_serializer = GetSchoolClassSerializer(school_class)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['PUT'])
@permission_classes([IsAuthenticated, IsSuperuser])
@authentication_classes([TokenAuthentication])
def assign_class_master(request, class_id, teacher_id):
    try:
        school_class = SchoolClass.objects.get(pk=class_id)
    except SchoolClass.DoesNotExist:
        msg = ["Class not found."]
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    try:
        teacher = Teacher.objects.get(pk=teacher_id)
    except Teacher.DoesNotExist:
        msg = ["Class master not found."]
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if not school_class.periods.filter(teacher=teacher).exists():
        msg = ["You can't make a teacher class master for a class they don't teach"]
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    if not school_class.year.is_active:
        msg = ["No current active year."]
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    old_master = school_class.master
    if old_master:
        old_master.is_class_master = False
        old_master.save()

    school_class.master = teacher
    teacher.is_class_master = True
    school_class.save()
    teacher.save()

    serializer = GetSchoolClassSerializer(school_class)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['PUT'])
@permission_classes([IsAuthenticated, IsSuperuser])
@authentication_classes([TokenAuthentication])
def assign_class_prefect(request, class_id, student_id):
    try:
        school_class = SchoolClass.objects.get(pk=class_id)
    except SchoolClass.DoesNotExist:
        msg = ["Class not found."]
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    try:
        student = Student.objects.get(student_id=student_id)
    except Teacher.DoesNotExist:
        msg = ["Class master not found."]
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if not school_class.year.is_active:
        msg = ["No current active year."]
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    old_prefect_id = school_class.prefect_id
    if old_prefect_id:
        old_prefect = Student.objects.get(pk=old_prefect_id)
        old_prefect.is_prefect = False
        old_prefect.save()

    school_class.prefect_id = student.id
    student.is_prefect = True
    school_class.save()
    student.save()
    serializer = GetSchoolClassSerializer(school_class)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
@authentication_classes([TokenAuthentication])
def get_class_teachers(request, class_id):
    try:
        school_class = SchoolClass.objects.get(pk=class_id)
    except SchoolClass.DoesNotExist:
        msg = ["Class not found."]
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if not school_class.year.is_active:
        msg = ["No current active year."]
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    periods = school_class.periods.all()

    class_master_periods = periods.filter(teacher__is_class_master=True)

    if class_master_periods.exists():
        class_master_obj = class_master_periods.first()
        class_master = {
            'id': class_master_obj.teacher.id,
            'name': class_master_obj.teacher.name,
        }
    else:
        class_master = None

    teachers = {"class": school_class.name,
                "tutors": [], 'master': class_master}

    for period in periods:
        teachers['tutors'].append({
            'id': period.teacher.id,
            'name': period.teacher.name,
            'is_class_master':
            period.teacher.is_class_master}
        )
    return Response(teachers, status=status.HTTP_200_OK)


@api_view(http_method_names=['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
@authentication_classes([TokenAuthentication])
def get_class_students(request, class_id):
    try:
        school_class = SchoolClass.objects.get(pk=class_id)
    except SchoolClass.DoesNotExist:
        msg = ["Class not found."]
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if not school_class.year.is_active:
        msg = ["No current active year."]
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    all_students = school_class.student_set.all()

    if all_students.filter(is_prefect=True).exists():
        prefect_obj = all_students.filter(is_prefect=True).first()
        prefect = {
            'id': prefect_obj.id,
            'name': prefect_obj.name,
            'student_id': prefect_obj.student_id
        }
    else:
        prefect = ""

    data = {"class": school_class.name, "students": [], 'prefect': prefect}

    for student in all_students:
        data['students'].append({
            'name': student.name,
            'student_id': student.student_id
        })
    return Response(data, status=status.HTTP_200_OK)
