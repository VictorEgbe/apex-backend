from datetime import datetime
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
from classes.models import SchoolClass
GENDER = (
    ('Male', 'Male'),
    ('Female', 'Female')
)


def upload_location(instance, filename):
    return f'students/{instance.name}-{filename}'


class Student(models.Model):
    name = models.CharField(max_length=150)
    student_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    address = models.CharField(null=True, blank=True, max_length=100)
    place_of_birth = models.CharField(null=True, blank=True, max_length=100)
    date_of_birth = models.DateField()
    student_id = models.CharField(
        max_length=25, null=True, blank=True, unique=True)
    gender = models.CharField(max_length=20, choices=GENDER)
    image = models.ImageField(upload_to=upload_location, blank=True, null=True)
    phone = PhoneNumberField(null=True, blank=True)
    parent_name = models.CharField(max_length=100, null=True, blank=True)
    parent_phone = PhoneNumberField()
    is_prefect = models.BooleanField(default=False)
    is_repeater = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(null=True, blank=True, unique=True)

    def get_age(self):
        year_of_birth = self.date_of_birth.year
        current_year = datetime.now().year
        return current_year - year_of_birth

    def get_image_url(self):
        return self.image.url if self.image else None

    def __str__(self):
        return f'{self.name} ({self.student_id})'

    class Meta:
        ordering = ['name']


@receiver(post_delete, sender=Student)
def delete_student_image(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete()
