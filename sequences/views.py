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
from terms.models import Term
from .serializers import CreateSequenceSerializer, GetSequenceSerializer
from .models import Sequence


@api_view(http_method_names=['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def create_sequence(request):

    if Sequence.objects.filter(is_active=True).exists():
        msg = ["You can not create a new sequence while another is active."]
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    try:
        term = Term.objects.get(is_active=True)
    except Term.DoesNotExist:
        msg = ["No active term. Please create an active term first."]
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    serializer = CreateSequenceSerializer(data=request.data)
    if serializer.is_valid():
        name = serializer.validated_data['name']

        if Sequence.objects.filter(name=name, term=term).exists():
            msg = ["Sequence with this name already exists."]
            return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

        sequence = serializer.save(term=term)
        sequence.slug = slugify(f'{sequence.pk}-{sequence.name}')
        sequence.save()
        response_serializer = GetSequenceSerializer(sequence)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_sequence(request, sequence_id):
    try:
        sequence = Sequence.objects.get(pk=sequence_id)
    except Sequence.DoesNotExist:
        msg = [f'Sequence not found.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSequenceSerializer(sequence)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ])
def get_sequences(request):
    # Get the sequences the current active year
    sequences = Sequence.objects.filter(
        term__year__is_active=True).order_by('-pk')
    serializer = GetSequenceSerializer(sequences, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_sequences_term(request, term_id):
    '''Returns all the sequence associated to a particular term'''
    try:
        term = Term.objects.get(pk=term_id)
    except Term.DoesNotExist:
        msg = ["Term not found."]
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    sequences = term.sequence_set.all()
    serializer = GetSequenceSerializer(sequences, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsSuperuser])
def delete_sequence(request, sequence_id):
    try:
        sequence = Sequence.objects.get(pk=sequence_id)
    except Sequence.DoesNotExist:
        msg = [f'Sequence not found.']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    if not sequence.is_active:
        msg = ["You can only delete active sequences."]
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    if not sequence.term.year.is_active:
        msg = ["You can only delete sequences in the current active year."]
        return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

    sequence.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@ api_view(http_method_names=['PUT'])
@ authentication_classes([TokenAuthentication])
@ permission_classes([IsAuthenticated, IsSuperuser])
def update_sequence(request):
    try:
        sequence = Sequence.objects.get(is_active=True)
    except Sequence.DoesNotExist:
        msg = ['Sequence not found']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    try:
        term = Term.objects.get(is_active=True)
    except Term.DoesNotExist:
        msg = ["Term not found."]
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    serializer = CreateSequenceSerializer(sequence, data=request.data)
    if serializer.is_valid():
        name = serializer.validated_data['name']
        short_name = serializer.validated_data['short_name']

        seq = Sequence.objects.filter(name=name, term=term)

        if seq.exists():
            sequence = seq.last()
            if sequence.short_name == short_name:
                msg = ["Sequence with this name already exists."]
                return Response({'error': msg}, status=status.HTTP_403_FORBIDDEN)

        serializer.save(term=term)
        updated_sequence = Sequence.objects.get(is_active=True)
        updated_sequence.slug = slugify(
            f'{updated_sequence.pk}-{updated_sequence.name}')
        updated_sequence.save()
        return Response(GetSequenceSerializer(updated_sequence).data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@ api_view(http_method_names=['PUT'])
@ authentication_classes([TokenAuthentication])
@ permission_classes([IsAuthenticated, IsSuperuser])
def deactivate_sequence(request):

    try:
        sequence = Sequence.objects.get(is_active=True)
    except Sequence.DoesNotExist:
        msg = ['Sequence not found']
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

    sequence.is_active = False
    sequence.save()

    return Response(status=status.HTTP_204_NO_CONTENT)
