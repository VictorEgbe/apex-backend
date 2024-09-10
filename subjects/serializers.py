from rest_framework import serializers
from .models import Subject, Period
from .formate_time import format_time


class GetSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class CreateSubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = '__all__'


class GetTeacherPeriodSerializer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField('get_subject')
    school_class = serializers.SerializerMethodField('get_school_class')
    start_time = serializers.SerializerMethodField('get_start_time')
    end_time = serializers.SerializerMethodField('get_end_time')

    class Meta:
        model = Period
        fields = [
            'id',
            'subject',
            'school_class',
            'start_time',
            'end_time',
            'number_of_periods',
            'day'
        ]

    def get_subject(self, period):
        return {
            'id': period.subject.id,
            'name': period.subject.name,
        }

    def get_school_class(self, period):
        school_class = period.school_class
        return {
            'id': school_class.id,
            'name': school_class.name,
        }

    def get_start_time(self, period):
        return format_time(period.start_time.strftime('%H:%M'))

    def get_end_time(self, period):
        return format_time(period.end_time.strftime('%H:%M'))
