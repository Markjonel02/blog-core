from rest_framework import serializers
from django.contrib.auth.models import User

from identity.models import Identity

from blog import settings
from oauth2_provider.models import (
    Application,
    RefreshToken,
    AccessToken
)
from datetime import (
    datetime,
    timedelta
)
from django.utils.crypto import get_random_string


class RegisterSerializer(serializers.ModelSerializer):
    # set all fields required and model
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']

        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True},
        }

    def validate(self, data):
        password = data['password']
        confirm_password = data['confirm_password']

        if password != confirm_password:
            raise serializers.ValidationError({"error_message": "Passwords do not match"})

        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'email', 'first_name', 'last_name', 'get_full_name']


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Identity
        fields = ['user', 'birthdate', 'gender', 'profile_picture']

