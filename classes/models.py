from django.db import models
from django.dispatch import receiver
from django.utils.text import slugify
from django.db.models.signals import pre_save
from years.models import Year
from teachers.models import Teacher

levels = (
    ('Ordinary', 'Ordinary'),
    ('Advanced', 'Advanced'),
)


class SchoolClass(models.Model):
    name = models.CharField(max_length=100)
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    short_name = models.CharField(max_length=50)
    level = models.CharField(max_length=15, choices=levels)
    master = models.OneToOneField(
        Teacher, on_delete=models.SET_NULL, null=True)
    prefect_id = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return f'{self.name} class of {self.year.name}'

    class Meta:
        verbose_name_plural = 'school classes'


@receiver(pre_save, sender=SchoolClass)
def create_slug(sender, instance, **kwargs):
    slug = f'{instance.pk}-{instance.name}-{instance.year.name}'
    instance.slug = slugify(slug)
