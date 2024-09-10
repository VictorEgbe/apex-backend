from rest_framework import serializers


class AbsenceDictField(serializers.DictField):
    child = serializers.CharField()


class AbsenceListField(serializers.ListField):
    child = AbsenceDictField(allow_empty=False)


class CreateOrUpdateAbsentSerializer(serializers.Serializer):

    '''class_list should be with two keys: student_id, is_absent and reason
    {"class_list": [
        {"student_id": "QIS3452", "is_absent": "false" }, 
        {"student_id": "QIS3450", "is_absent": "true" }
    ],
    "date": "2024-06-06"
    '''
    class_list = AbsenceListField(allow_empty=False)
    date = serializers.DateField()


class TeacherCreateOrUpdateAbsentSerializer(serializers.Serializer):
    date = serializers.DateField()
    is_absent = serializers.BooleanField()
