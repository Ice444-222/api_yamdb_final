from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers

from reviews.models import Category, Genre, Title
from users.models import User


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        ]

    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except ValidationError:
            return Response(
                {"error":
                 "Отсутствует обязательное поле или оно не корректно"
                 },
                status=status.HTTP_400_BAD_REQUEST
            )


class UserCreateSerializer(UserBasicSerializer):
    class Meta:
        model = User
        fields = ['email', 'username']


class UserRetrieveUpdateSerializer(UserBasicSerializer):
    role = serializers.ReadOnlyField()


class UserRetrieveUpdateDestroySerializer(UserBasicSerializer):

    class Meta:
        model = User
        fields = '__all__'


class CustomTokenObtainPairSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)

    def validate(self, attrs):
        confirmation_code = attrs.get('confirmation_code')
        username = attrs.get('username')
        if confirmation_code and username:
            try:
                user = User.objects.get(
                    confirmation_code=confirmation_code, username=username
                )
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    'Неверные данные для выдачи токена.'
                )
        if user:
            refresh = RefreshToken.for_user(user)
            attrs['user'] = user
            attrs['access'] = str(refresh.access_token)
            attrs['refresh'] = str(refresh)
        return attrs

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Title