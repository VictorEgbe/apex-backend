from django.db import models
from accounts.models import User
from departments.models import Department


class Teacher(User):
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="teachers")
    is_hod = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=True)
    is_class_master = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-pk', )
