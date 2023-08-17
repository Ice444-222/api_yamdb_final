from django.contrib.auth import get_user_model

from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.exceptions import (
    NotFound,
    PermissionDenied,
    AuthenticationFailed
)
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import ListAPIView

from reviews.models import Categories, Genres, Title
from users.models import User

from .filters import TitlesFilter
from .permissions import (
    IsAdmin,
    IsAuthorOrAdminOrModeratorOrReadOnly,
    ReadOnly,
    IsAdminOrReadOnly
)
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    UserBasicSerializer,
    UserCreateSerializer,
    UserRetrieveUpdateDestroySerializer,
    UserRetrieveUpdateSerializer
)
from .viewsets import CreateListDestroyViewSet


User = get_user_model()


class BasicUserCreateView(generics.CreateAPIView):

    def perform_create(self, serializer):
        user = serializer.save()
        user.generate_confirmation_code()
        user.save()


class BasicUserUpdateView(generics.RetrieveUpdateDestroyAPIView):
    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class UserCreateView(BasicUserCreateView):
    permission_classes = (permissions.AllowAny,)

    queryset = User.objects.all()
    serializer_class = UserCreateSerializer


class UserListCreateView(BasicUserCreateView, ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserRetrieveUpdateDestroySerializer
    permission_classes = IsAdmin
    filter_backends = (filters.SearchFilter,)
    pagination_class = PageNumberPagination
    search_fields = ("username",)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserBasicSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except PermissionDenied:
            raise PermissionDenied("Нет прав доступа")
        except AuthenticationFailed:
            raise AuthenticationFailed("Необходим JWT-токен")

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except PermissionDenied:
            raise PermissionDenied("Нет прав доступа")
        except AuthenticationFailed:
            raise AuthenticationFailed("Необходим JWT-токен")


class UserRetrieveUpdateDestroyView(
    generics.RetrieveDestroyAPIView, BasicUserUpdateView
):
    serializer_class = UserRetrieveUpdateDestroySerializer
    permission_classes = IsAdmin
    queryset = User.objects.all()

    def get_object(self):
        username = self.kwargs.get("username")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound("Пользователь не найден")
        except PermissionDenied:
            raise PermissionDenied("Нет прав доступа")
        except AuthenticationFailed:
            raise AuthenticationFailed("Необходим JWT-токен")
        return user

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response(
            {"message": "Удачное выполнение запроса"},
            status=status.HTTP_204_NO_CONTENT,
        )


class UserRetrieveUpdateView(generics.RetrieveAPIView, BasicUserUpdateView):
    queryset = User.objects.all()
    serializer_class = UserRetrieveUpdateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        confirmation_code = request.data.get("confirmation_code")
        username = request.data.get("username")
        if confirmation_code is None or username is None:
            return Response(
                {
                    "error": (
                        "Отсутствует обязательное поле или оно некорректно."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(
                confirmation_code=confirmation_code, username=username
            )
        except User.DoesNotExist:
            raise NotFound("Пользователь не найден")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data.get("access")
            refresh_token = serializer.validated_data.get("refresh")
            response_data = {
                "ID пользователя": user.id,
                "token": str(token),
                "Обновление токена": str(refresh_token),
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoriesGenresViewSet(CreateListDestroyViewSet):
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter,)
    search_fields = ("name",)
    permission_classes = IsAdminOrReadOnly
    lookup_field = "slug"


class CategoryViewSet(CategoriesGenresViewSet):

    queryset = Categories.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoriesGenresViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = PageNumberPagination
    permission_classes = IsAdminOrReadOnly
    ordering_fields = ("name",)
    filterset_class = TitlesFilter
