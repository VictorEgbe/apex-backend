from django.db .models import Case, When
from .models import Period
from django.db import models


def get_ordered_periods(teacher_id):
    order = Case(
        When(day='Monday', then=1),
        When(day='Tuesday', then=2),
        When(day='Wednesday', then=3),
        When(day='Thursday', then=4),
        When(day='Friday', then=5),
        When(day='Saturday', then=6),
        When(day='Sunday', then=7),

        output_field=models.IntegerField(),
    )

    return Period.objects.filter(teacher__id=teacher_id).annotate(day_order=order).order_by('day_order')
