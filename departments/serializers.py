from rest_framework import serializers
from teachers.serializers import GetTeacherSerializer
from .models import Department


class GetDepartmentSerializer(serializers.ModelSerializer):
    teachers = serializers.SerializerMethodField('get_teachers')
    hod = serializers.SerializerMethodField('get_hod')

    class Meta:
        model = Department
        fields = (
            'id',
            'name',
            'teachers',
            'hod',
            'slug',
        )

    def get_teachers(self, department):
        tutors = department.teachers.all()
        teachers = GetTeacherSerializer(tutors, many=True)
        females = tutors.filter(gender='Female').count()
        males = tutors.filter(gender='Male').count()
        total = tutors.count()

        return {
            'total': total,
            'males': males,
            'females': females,
            'teachers': teachers.data
        }

    def get_hod(self, department):
        try:
            teacher = department.teachers.get(pk=department.hod_id)
        except:
            return None

        return GetTeacherSerializer(teacher).data


class CreateDepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ('name', )


class AllDepartmentsSerializer(serializers.ModelSerializer):
    teachers_stats = serializers.SerializerMethodField('get_teachers_stats')
    hod = serializers.SerializerMethodField('get_hod')

    class Meta:
        model = Department
        fields = ('id', 'name', 'hod', 'teachers_stats', 'slug')

    def get_hod(self, department):
        try:
            teacher = department.teachers.get(pk=department.hod_id)
        except:
            return None

        return GetTeacherSerializer(teacher).data

    def get_teachers_stats(self, department):
        teachers = department.teachers.all()
        females = teachers.filter(gender='Female').count()
        males = teachers.filter(gender='Male').count()
        total = teachers.count()

        return {
            'total': total,
            'males': males,
            'females': females
        }
