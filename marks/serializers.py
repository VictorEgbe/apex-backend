from rest_framework import serializers

from .models import Mark


class GetMarkSerializer(serializers.ModelSerializer):
    score = serializers.SerializerMethodField('get_score')
    teacher = serializers.SerializerMethodField('get_teacher')
    student = serializers.SerializerMethodField('get_student')
    subject = serializers.SerializerMethodField('get_subject')
    student_class = serializers.SerializerMethodField('get_class_name')
    sequence = serializers.SerializerMethodField('get_sequence')

    def get_score(self, mark):
        return round(float(mark.score), 2)

    def get_teacher(self, mark):
        return mark.teacher.name

    def get_student(self, mark):
        return mark.student.name

    def get_class_name(self, mark):
        return mark.student.student_class.name

    def get_subject(self, mark):
        return mark.subject.name

    def get_sequence(self, mark):
        return mark.sequence.name

    class Meta:
        model = Mark
        fields = '__all__'


# class MarkDictField(serializers.DictField):
#     child = serializers.CharField()


# class MarkListField(serializers.ListField):
#     child = MarkDictField(allow_empty=False)


class CreateOrUpdateMarkSerializer(serializers.Serializer):
    '''class_list should be with two keys: student_id and score'''
    '''e.g {"student_id": "QIS3452", "score": 12.5}'''

    # class_list = MarkListField(allow_empty=False)
    class_list = serializers.ListField(allow_empty=False)
    competency = serializers.CharField()
