from django.db import models
from django.contrib.auth.models import User


class Identity(models.Model):
    class ProfileManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().select_related('user')

    MALE = 'M'
    FEMALE = 'F'
    NA = 'N/A'

    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (NA, 'N/A'),
    ]

    birthdate = models.DateField(null=True)
    profile_picture = models.ImageField(upload_to='profile-pictures/', blank=True, null=True)
    user = models.OneToOneField(User, related_name='identity', on_delete=models.CASCADE)
    gender = models.CharField(max_length=5, choices=GENDER_CHOICES, default=NA)

    objects = ProfileManager()

    def __str__(self):
        return self.user.username


