from django.db import models

from terms.models import Term


class Sequence(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        string = f'{self.name}: {self.term.year.name}'
        return string
