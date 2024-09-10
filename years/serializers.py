from rest_framework import serializers

from .models import Year


class CreateYearSerializer(serializers.ModelSerializer):

    class Meta:
        model = Year
        fields = ['name']


class GetYearSerializer(serializers.ModelSerializer):

    class Meta:
        model = Year
        fields = ['id', 'name', 'is_active', 'slug']
