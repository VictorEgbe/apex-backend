from django.utils.translation import gettext as _
from rest_framework import serializers
from .models import Term


class CreateTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ['name']

    def save(self, **kwargs):
        year = kwargs['year']
        name = self.validated_data['name']

        term, created = Term.objects.get_or_create(name=name, year=year)
        if not created:
            error_msg = {'error': _(
                f'{name} already created for the year {year.name}')}
            raise serializers.ValidationError(error_msg)
        return term


class GetTermSerializer(serializers.ModelSerializer):

    year = serializers.SerializerMethodField()

    def get_year(self, term):
        return term.year.name

    class Meta:
        model = Term
        fields = '__all__'


class UpdateTermSerializer(serializers.Serializer):
    name = serializers.CharField()
