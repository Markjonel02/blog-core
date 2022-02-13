from django.shortcuts import render
from rest_framework import generics, permissions, response, status
from .models import Identity
from .serializers import RegisterSerializer, ProfileSerializer
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope


class RegisterView(generics.CreateAPIView):
    permission_classes = []
    queryset = Identity.objects.all()
    serializer_class = RegisterSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    serializer_class = ProfileSerializer

    def get_object(self):
        user = self.request.user
        if Identity.objects.filter(user=user).exists():
            return user.identity
        else:
            user.identity = Identity(user=user)
            user.save()
            return user.identity

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'request': self.request
        })
        return context


