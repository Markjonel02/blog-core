from django.db import models
from django.contrib.auth.models import User


class Identity(models.Model):

    MALE = 'M'
    FEMALE = 'F'

    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    ]

    birthdate = models.DateField(null=True)
    profile_picture = models.ImageField(upload_to='profile-pictures/', blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=MALE)

    def __str__(self):
        return self.user.last_name
