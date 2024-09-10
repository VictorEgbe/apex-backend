from rest_framework import serializers
from .models import Student


class GetStudentSerializer(serializers.ModelSerializer):
    student_class = serializers.SerializerMethodField('get_student_class')
    age = serializers.SerializerMethodField('get_age')
    image = serializers.SerializerMethodField('get_image_url')
    phone = serializers.SerializerMethodField('get_phone')
    parent_phone = serializers.SerializerMethodField('get_parent_phone')

    class Meta:
        model = Student
        fields = '__all__'

    def get_student_class(self, student):
        return {
            'id': student.student_class.pk,
            'name': student.student_class.name,
            'slug': student.student_class.slug
        }

    def get_age(self, student):
        return student.get_age()

    def get_image_url(self, student):
        return student.get_image_url()

    def get_phone(self, student):
        if student.phone:
            return student.phone.as_national
        return None

    def get_parent_phone(self, student):
        if student.parent_phone:
            return student.parent_phone.as_national
        return None


class CreateStudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = [
            'name',
            'date_of_birth',
            'gender',
            'image',
            'phone',
            'parent_name',
            'parent_phone',
            "address",
            "place_of_birth",
            "is_repeater",
        ]


class ChangeStudentImageSerializer(serializers.Serializer):
    image = serializers.ImageField()
