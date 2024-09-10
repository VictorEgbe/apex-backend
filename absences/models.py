from django.db import models

from students.models import Student
from sequences.models import Sequence
from teachers.models import Teacher
from subjects.models import Period


class StudentAbsence(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="absences")
    date = models.DateField()
    sequence = models.ForeignKey(
        Sequence, on_delete=models.CASCADE, related_name="absences")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.student.name} on {self.date}'


class TeacherAbsence(models.Model):
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="absences")
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    date = models.DateField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.teacher.name} on {self.date}'
