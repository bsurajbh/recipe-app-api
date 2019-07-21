from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class UserSerializer(serializers.ModelSerializer):
    """user class serialiser"""
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """create new user"""
        return get_user_model().objects.create_user(**validated_data)


class AuthtokenSerializer(serializers.Serializer):
    """auth token serialiser """
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'}, trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # check if user exists
        user_exists = get_user_model().objects.filter(email=email)
        # raise exception if user does not exists
        if not user_exists:
            msg = _('user does not exists')
            raise serializers.ValidationError(
                {'email': msg}, code='authentication')
        user = authenticate(
            request=self.context.get('request'), username=email,
            password=password
        )
        if not user:
            msg = _('plase provide correct credentials')
            raise serializers.ValidationError(
                {'email': msg}, code='authentication')

        attrs['user'] = user
        return attrs
