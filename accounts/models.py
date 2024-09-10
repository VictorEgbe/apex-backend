from datetime import date
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from django.utils.text import slugify


from phonenumber_field.modelfields import PhoneNumberField

GENDER = (
    ('Male', 'Male'),
    ('Female', 'Female')
)


def upload_location(instance, filename):
    return f'accounts/{filename}-{instance.pk}'


class User(AbstractUser):
    phone = PhoneNumberField(unique=True, blank=False, null=False, error_messages={
        "unique": _("A user with that phone number already exists."),
        "required": _("A valid phone number is required."),
    })
    address = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(choices=GENDER, max_length=6)
    date_of_birth = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to=upload_location, blank=True, null=True)
    name = models.CharField(_("name"), max_length=180)
    email = models.EmailField(_("email address"), unique=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    special_role = models.CharField(max_length=50, blank=True, null=True)
    title_name = models.CharField(max_length=50, null=True, blank=True)
    marital_status = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    is_superuser = models.BooleanField(default=False)
    username = models.CharField(
        _("username"),
        max_length=150,
        null=True,
        blank=True,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[UnicodeUsernameValidator()],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email', 'name', 'gender', 'username']

    def __str__(self):
        return self.name if self.name else str(self.phone.as_national)

    @property
    def get_image_url(self):
        if self.image:
            return self.image.url
        return None

    def get_age(self):
        if self.date_of_birth:
            year_of_birth = self.date_of_birth.year
            current_year = date.today().year
            return current_year - year_of_birth
        return None


@receiver(post_delete, sender=User)
def deleted_user_image(sender, instance, **kwargs):
    if instance.image and instance.is_admin:
        instance.image.delete()


@receiver(post_save, sender=User)
def set_super_user_stuffs(sender, instance, created, **kwargs):
    if instance.is_superuser and created:
        instance.is_admin = True
        instance.slug = slugify(f'{instance.pk}-{instance.name}')
        instance.date_of_birth = date.today()
        instance.save()
