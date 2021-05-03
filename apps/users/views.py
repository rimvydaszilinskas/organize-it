from rest_framework import generics

from .serializers import UserAuthenticationSerializer, UserRegistrationSerializer


class UserAuthenticationView(generics.CreateAPIView):
    serializer_class = UserAuthenticationSerializer
    authentication_classes = []


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    authentication_classes = []
