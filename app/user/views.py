from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import generics
from rest_framework.settings import api_settings
from user.serialisers import UserSerializer, AuthtokenSerializer
# Create your views here.


class createUseriew(generics.CreateAPIView):
    """create user """
    serializer_class = UserSerializer


class createTokenView(ObtainAuthToken):
    """token for user"""
    serializer_class = AuthtokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
