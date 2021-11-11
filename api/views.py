import datetime as dt

import jwt
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .filters import TitlesFilter
from .models import Category, Genre, Review, Title, User
from .permissions import (HasUsernameForPOST, IsAdmin, IsAdminOrReadOnly,
                          IsStaffOrAuthorOrReadOnly)
from .serializers import (CategoriesSerializer, CommentsSerializer,
                          GenresSerializer, ReviewsSerializer,
                          SendConfirmCodeSerializer,
                          TitlesSafeMethodSerializer,
                          TitlesUnSafeMethodSerializer, TokenReceiveSerializer,
                          UserSerializer)

MAIL_SUBJECT = 'Код подтверждения'
MAIL_DESCRIPTION = ('Для получения токена отправьте email и confirmation_code'
                    ' на адрес "api/v1/auth/token/". Ваш confirmation_code: ')


def create_jwt(email):
    """
    Create and sign a confirmation_code like a JSON Web Token.
    Payload is an email and an expiration time.
    """
    secret_key = settings.SECRET_KEY
    expire = dt.datetime.utcnow() + settings.EMAIL_EXPIRATION_TIME
    payload = {'email': email, 'exp': expire}
    signed_token = jwt.encode(payload=payload, key=secret_key,
                              algorithm='HS256')
    return signed_token


@api_view(('POST',))
@permission_classes((AllowAny,))
def send_confirmation_code_view(request):
    serializer = SendConfirmCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get('email')
    signed_code = create_jwt(email)
    send_mail(subject=MAIL_SUBJECT, from_email=settings.DEFAULT_FROM_EMAIL,
              message=MAIL_DESCRIPTION + signed_code,
              recipient_list=(email,), fail_silently=True)
    return Response(serializer.validated_data,
                    status=status.HTTP_200_OK)


@api_view(('POST',))
@permission_classes((AllowAny,))
# Невозможно указать throttle_scope,
# а для класса ScopedRateThrottle это необходимо.
def token_receive_view(request):
    serializer = TokenReceiveSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
    email = serializer.validated_data.get('email')
    user, _ = User.objects.get_or_create(email=email)

    access = str(AccessToken.for_user(user))
    return Response({'token': access}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.exclude(username__isnull=True)
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    search_fields = ('username',)
    lookup_field = 'username'
    throttle_scope = 'burst-non-employee'

    @action(detail=False, methods=('get', 'patch'),
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(instance=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(instance=request.user,
                                         data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializer
    permission_classes = (IsStaffOrAuthorOrReadOnly, HasUsernameForPOST)
    throttle_scope = 'burst-non-employee'

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.order_by('-id')

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer
    permission_classes = (IsStaffOrAuthorOrReadOnly, HasUsernameForPOST)
    throttle_scope = 'burst-non-employee'

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id')
        )
        return review.comments.order_by('-id')

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, review=review)


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    throttle_scope = 'burst-non-employee'
    search_fields = ('=name',)
    lookup_field = 'slug'


class CategoriesViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.order_by('name')
    serializer_class = CategoriesSerializer


class GenresViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.order_by('name')
    serializer_class = GenresSerializer


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('-id')
    permission_classes = (IsAdminOrReadOnly,)
    throttle_scope = 'burst-non-employee'
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitlesFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitlesSafeMethodSerializer
        return TitlesUnSafeMethodSerializer
