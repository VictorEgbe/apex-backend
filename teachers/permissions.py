from rest_framework import permissions
from .models import Teacher


class IsTeacher(permissions.BasePermission):
    """
    Custom permission to only allow access to teachers only.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated and is an teacher
        try:
            teacher = Teacher.objects.get(pk=request.user.pk)
        except Teacher.DoesNotExist:
            return False
        return request.user and request.user.is_authenticated and teacher.is_teacher
