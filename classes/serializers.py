from django.db.models import Count, Q
from rest_framework import serializers
from students.models import Student
from .models import SchoolClass


class CreateSchoolClassSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    short_name = serializers.CharField(required=True)
    level = serializers.CharField(required=True)


class GetSchoolClassSerializer(serializers.ModelSerializer):
    year = serializers.SerializerMethodField('get_year')
    master = serializers.SerializerMethodField('get_master')
    prefect = serializers.SerializerMethodField('get_prefect')
    students = serializers.SerializerMethodField('get_class_students_stats')

    def get_year(self, school_class):
        year = school_class.year
        return year.name

    def get_master(self, school_class):
        master = school_class.master
        if master:
            return {
                'id': master.id,
                'name': master.name,
                'image': master.get_image_url,
                'gender': master.gender
            }
        return None

    def get_prefect(self, school_class):
        if school_class.student_set.filter(is_prefect=True).exists():
            prefect = school_class.student_set.filter(is_prefect=True).first()
            return {
                'id': prefect.id,
                'name': prefect.name,
                'image': prefect.get_image_url(),
                'gender': prefect.gender
            }
        return None

    def get_class_students_stats(self, school_class):
        return school_class.student_set.all().aggregate(
            total=Count('id'),
            males=Count('id', filter=Q(gender='Male')),
            females=Count('id', filter=Q(gender='Female'))
        )

    class Meta:
        model = SchoolClass
        fields = '__all__'


class GetSimpleSchoolClassSerializer(serializers.ModelSerializer):
    year = serializers.SerializerMethodField('get_year')
    students_count = serializers.SerializerMethodField(
        'get_class_students_stats')

    def get_year(self, school_class):
        year = school_class.year
        return year.name

    def get_class_students_stats(self, school_class):
        return school_class.student_set.all().aggregate(
            total=Count('id'),
            males=Count('id', filter=Q(gender='Male')),
            females=Count('id', filter=Q(gender='Female'))
        )

    class Meta:
        model = SchoolClass
        fields = [
            'id',
            'name',
            'year',
            'students_count',
            'short_name',
            'slug',
            'level'
        ]


class UpdateSchoolClassInfoSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    short_name = serializers.CharField(required=True)
    level = serializers.CharField(required=True)
