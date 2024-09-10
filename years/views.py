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
from accounts.permissions import IsSuperuser, IsAdminUser
from .models import Year
from .serializers import CreateYearSerializer, GetYearSerializer
from teachers.models import Teacher
from accounts.models import User
from students.models import Student


@api_view(http_method_names=['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def create_year(request):
    if Year.objects.filter(is_active=True).exists():
        msg = [f"You can't create a new academic year while another is still active."]
        return Response({'error': msg}, status=status.HTTP_401_UNAUTHORIZED)
    serializer = CreateYearSerializer(data=request.data)
    if serializer.is_valid():
        year = serializer.save()
        year.slug = slugify(f'{year.id}-{year.name}')
        year.save()
        data = GetYearSerializer(year).data
        return Response(data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_year(request, year_id):
    try:
        year = Year.objects.get(id=year_id)
    except Year.DoesNotExist:
        msg = ['Academic year not found']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetYearSerializer(year)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def update_year(request, year_id):
    try:
        year = Year.objects.get(id=year_id)
    except Year.DoesNotExist:
        msg = ['Academic year not found']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if not year.is_active:
        msg = [f"You can't update an inactive year."]
        return Response({'error': msg}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = CreateYearSerializer(year, data=request.data)
    if serializer.is_valid():
        updated_year = serializer.save()
        data = GetYearSerializer(updated_year).data
        return Response(data, status=status.HTTP_202_ACCEPTED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def delete_year(request, year_id):
    try:
        year = Year.objects.get(id=year_id)
    except Year.DoesNotExist:
        msg = ['Academic year not found']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if year.is_active:
        msg = [f"You can't delete an academic year while it's active."]
        return Response({'error': msg}, status=status.HTTP_401_UNAUTHORIZED)

    year.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_years(request):
    years = Year.objects.all()
    response_data = []

    for year in years:
        students = Student.objects.filter(student_class__year=year).count()
        terms = year.term_set.all().count()

        sequences = 0
        for term in year.term_set.all():
            sequences += term.sequence_set.all().count()

        response_data.append({
            'id': year.id,
            'slug': year.slug,
            'name': year.name,
            'is_active': year.is_active,
            'students': students,
            'terms': terms,
            'sequences': sequences,
        })
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(http_method_names=['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def deactivate_year(request):
    try:
        year = Year.objects.get(is_active=True)
    except Year.DoesNotExist:
        msg = ['No active academic year. Please create a year.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    terms = year.term_set.all().count()

    sequences = 0
    for term in year.term_set.all():
        sequences += term.sequence_set.all().count()

    if (terms < 3):
        msg = ['Cannot deactivate year with less than 3 terms.']
        return Response({'error': msg}, status=status.HTTP_400_BAD_REQUEST)

    if (sequences < 6):
        msg = ['Cannot deactivate year with less than 6 sequences.']
        return Response({'error': msg}, status=status.HTTP_400_BAD_REQUEST)

    for term in terms:
        for seq in term.sequence_set.all():
            seq.is_active = False
            seq.save()

        term.is_active = False
        term.save()

    year.is_active = False
    year.save()
    data = GetYearSerializer(year).data
    return Response(data, status=status.HTTP_200_OK)
