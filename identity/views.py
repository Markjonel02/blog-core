from rest_framework import generics, permissions, response, status
from blog import settings
from .models import Identity
from .serializers import RegisterSerializer, ProfileSerializer
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
from django.contrib.auth.models import User


class RegisterView(generics.CreateAPIView):
    permission_classes = []
    queryset = Identity.objects.all()
    serializer_class = RegisterSerializer

    def create_access_token(self, user):
        application = Application.objects.all()

        if application.exists():
            self.expire_seconds = settings.OAUTH2_PROVIDER['ACCESS_TOKEN_EXPIRE_SECONDS']
            scopes = settings.OAUTH2_PROVIDER['SCOPES']
            expires = datetime.now() + timedelta(seconds=self.expire_seconds)
            token = get_random_string(32)
            refresh_token = get_random_string(32)

            access_token = AccessToken.objects.create(
                user=user,
                expires=expires,
                scope=scopes,
                token=token,
                application=application.first(),
            )

            refresh_token = RefreshToken.objects.create(
                user=user,
                access_token=access_token,
                token=refresh_token,
                application=application.first(),
            )

            return access_token, refresh_token

        return None

    def post(self, request, *args, **kwargs):
        password = request.data.get('password')
        email = request.data.get('email')
        username = request.data.get('username')

        user = User.objects.create(username=username, email=email)
        user.set_password(password)
        user.save()

        # create identity/profile
        Identity.objects.create(user=user)

        oauth_token, refresh_token = self.create_access_token(
            user)

        data = {
            "access_token": oauth_token.token,
            "expires": self.expire_seconds,
            "token_type": "Bearer",
            "scope": oauth_token.scope,
            "refresh_token": refresh_token.token
        }

        return response.Response(
            data=data,
            status=status.HTTP_200_OK
        )

        return super().post(request, *args, **kwargs)


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    serializer_class = ProfileSerializer

    def get_object(self):
        user = self.request.user
        if Identity.objects.filter(user=user).exists():
            return user.identity
        else:
            user.identity = Identity(user=user)
            user.identity.save()
            return user.identity

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'request': self.request
        })
        return context


