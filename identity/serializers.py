import base64
from rest_framework import serializers
from django.contrib.auth.models import User
from identity.models import Identity
from django.utils.crypto import get_random_string
from django.core.files.base import ContentFile


def get_random_code():
    return get_random_string(
        length=5,
        allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    )


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
        fields = (
            'pk',
            'email',
            'first_name',
            'last_name',
            'get_full_name'
        )

        extra_kwargs = {
            'username': {
                'read_only': True
            },
        }


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    profile_picture_image_64 = serializers.CharField(allow_null=True, required=False)

    class Meta:
        model = Identity
        fields = ('user', 'birthdate', 'gender', 'profile_picture', 'profile_picture_image_64')

        extra_kwargs = {
            'profile_picture': {
                'read_only': True
            }
        }

    def validate(self, attrs):
        user = attrs.get('user', None)
        # get request context
        request = self.context['request']

        errors = {}
        if user:
            email = user.get('email', None)
            if email:
                if User.objects.filter(email=email).exclude(pk=request.user.pk).exists():
                    errors['email'] = "Email address is already taken"

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def update(self, instance, validated_data):
        def extract_file(base64_string, image_type):
            img_format, img_str = base64_string.split(';base64,')
            ext = img_format.split('/')[-1]
            return f"{instance}-{get_random_code()}-{image_type}.{ext}", ContentFile(base64.b64decode(img_str))

        profile_picture_image = validated_data.get('profile_picture_image_64', None)

        if profile_picture_image:
            filename, data = extract_file(profile_picture_image, 'profile_picture')
            instance.profile_picture.save(filename, data, save=True)

        user = instance.user
        user_data = validated_data.pop('user')

        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        user.email = user_data.get('email', user.email)

        instance.save()

        return instance

