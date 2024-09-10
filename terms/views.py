from django.db.models import Count
from django.utils.text import slugify
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from knox.auth import TokenAuthentication
from accounts.permissions import IsSuperuser, IsAdminUser
from years.models import Year
from .models import Term
from .serializers import (
    CreateTermSerializer,
    GetTermSerializer,
    UpdateTermSerializer
)


@api_view(http_method_names=['POST'])
@permission_classes([IsAuthenticated, IsSuperuser])
@authentication_classes([TokenAuthentication])
def create_term(request):

    if Term.objects.filter(is_active=True).exists():
        msg = [f"You can't create a new term while another is still active."]
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    try:
        year = Year.objects.get(is_active=True)
    except Year.DoesNotExist:
        msg = ["Please create an active year first."]
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    serializer = CreateTermSerializer(data=request.data)
    if serializer.is_valid():
        name = serializer.validated_data['name']

        if Term.objects.filter(name=name, year=year).exists():
            msg = ["Term with this name already exists."]
            return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

        term = serializer.save(year=year)
        term.slug = slugify(f'{term.pk}-{term.name}')
        term.save()
        data = GetTermSerializer(term).data
        return Response(data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
@authentication_classes([TokenAuthentication])
def get_term(request, term_id):
    try:
        term = Term.objects.get(pk=term_id)
    except Term.DoesNotExist:
        msg = ["Term not found."]
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)
    serializer = GetTermSerializer(term)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
@authentication_classes([TokenAuthentication])
def get_terms(request):
    terms = Term.objects.all().order_by('-pk')
    terms_data = terms.values(
        'id',
        'name',
        'year__name',
        'is_active',
        'slug').annotate(sequences_count=Count('sequence'))
    response_data = list(terms_data)
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(http_method_names=['PUT'])
@permission_classes([IsAuthenticated, IsSuperuser])
@authentication_classes([TokenAuthentication])
def update_term(request, term_id):
    try:
        term = Term.objects.get(pk=term_id)
    except Term.DoesNotExist:
        msg = ["Term not found."]
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if not term.is_active:
        msg = [f"You can't update an inactive term."]
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    if not term.year.is_active:
        msg = [f"You can't update a term for an inactive year."]
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    serializer = UpdateTermSerializer(data=request.data)

    if serializer.is_valid():
        name = serializer.validated_data['name']
        if Term.objects.filter(name=name, year=term.year).exists():
            msg = [f'{name} already exists for the year {term.year.name}']
            return Response({'error': msg}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            term.name = name
            term.slug = slugify(f'{term.pk}-{term.name}')
            term.save()
            data = GetTermSerializer(term).data
            return Response(data, status=status.HTTP_200_OK)

    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['DELETE'])
@permission_classes([IsAuthenticated, IsSuperuser])
@authentication_classes([TokenAuthentication])
def delete_term(request, term_id):
    try:
        term = Term.objects.get(pk=term_id)
    except Term.DoesNotExist:
        msg = "Term not found."
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if term.is_active:
        msg = f"You can't delete a term while it's active."
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    term.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(http_method_names=['PUT'])
@permission_classes([IsAuthenticated, IsSuperuser])
@authentication_classes([TokenAuthentication])
def deactivate_term(request):
    try:
        term = Term.objects.get(is_active=True)
    except Term.DoesNotExist:
        msg = ["No active term not found. Please create a term"]
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    term_sequences = term.sequence_set.all().count()
    if term_sequences < 2:
        msg = ["You can't deactivate a term with less than 2 sequences"]
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    term.is_active = False
    term.save()
    data = GetTermSerializer(term).data
    return Response(data, status=status.HTTP_200_OK)
