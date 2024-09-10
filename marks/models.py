from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from teachers.models import Teacher
from students.models import Student
from subjects.models import Subject
from sequences.models import Sequence


class Mark(models.Model):
    score = models.DecimalField(max_digits=5, decimal_places=3, validators=[
                                MinValueValidator(0), MaxValueValidator(20)])
    teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="marks")
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="marks")
    sequence = models.ForeignKey(
        Sequence, on_delete=models.CASCADE, related_name="marks")
    competency = models.CharField(max_length=300, null=True, blank=True)
    grade = models.CharField(max_length=10, null=True, blank=True)
    remark = models.CharField(max_length=30, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        student = self.student.name
        student_class = self.student.student_class.name
        subject = self.subject.name
        string = f'{student}: {self.score} on 20 in {student_class} {subject}'
        return string
