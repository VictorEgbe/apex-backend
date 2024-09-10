from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from classes.models import SchoolClass
from teachers.models import Teacher
COEFFICIENT = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
)

days = (('Monday', 'Monday'), ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'),
        ('Saturday', 'Saturday'), ('Sunday', 'Sunday'))

levels = (
    ('Ordinary', 'Ordinary'),
    ('Advanced', 'Advanced'),
)


class Subject(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50)
    coefficient = models.PositiveSmallIntegerField(
        choices=COEFFICIENT, validators=[MinValueValidator(1), MaxValueValidator(5)])
    level = models.CharField(max_length=15, choices=levels)
    slug = models.SlugField(null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}, coefficient {self.coefficient}'


class Period(models.Model):
    number_of_periods = models.PositiveSmallIntegerField()
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name='periods')
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name='periods')
    school_class = models.ForeignKey(
        SchoolClass, on_delete=models.CASCADE, related_name="periods")
    day = models.CharField(max_length=10, choices=days)
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        subject = self.subject.name
        subject_class = self.school_class.name
        day = self.day
        teacher = self.teacher.name
        periods = 'periods' if self.number_of_periods > 1 else 'period'
        return f'{subject}, {subject_class} by {teacher} on {day} ({self.number_of_periods} {periods})'
