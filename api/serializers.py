import jwt
from rest_framework import serializers

from django.conf import settings

from .models import Category, Comment, Genre, Review, Title, User


class SendConfirmCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()


class TokenReceiveSerializer(serializers.Serializer):
    email = serializers.EmailField()
    confirmation_code = serializers.CharField()

    def validate(self, attrs):
        signed_token = attrs.get('confirmation_code')
        secret_key = settings.SECRET_KEY
        try:
            payload = jwt.decode(jwt=signed_token, key=secret_key,
                                 algorithms=('HS256',))
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('Код подтверждения устарел')
        except jwt.InvalidTokenError:
            raise serializers.ValidationError('Неверный код подтверждения')

        email_from_token = payload.get('email')
        open_email = attrs['email']
        if open_email != email_from_token:
            raise serializers.ValidationError('Почта не совпадает')

        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'bio', 'email', 'role')
        extra_kwargs = {'username': {'required': True}}

    def validate_role(self, role):
        message = 'Только администратор может менять роль.'
        changer = self.context['request'].user
        if not changer.is_admin:
            raise serializers.ValidationError(message)
        return role


class ReviewsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    score = serializers.IntegerField(min_value=1, max_value=10)

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        author = self.context['request'].user
        title_id = self.context['view'].kwargs.get('title_id')
        if Review.objects.filter(title_id=title_id, author=author).exists():
            raise serializers.ValidationError('Отзыв уже существует')
        return data

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = '__all__'


class TitlesUnSafeMethodSerializer(TitleBaseSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all(),
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        required=False
    )


class TitlesSafeMethodSerializer(TitleBaseSerializer):
    genre = GenresSerializer(many=True)
    category = CategoriesSerializer()
    rating = serializers.DecimalField(max_digits=3, decimal_places=2,
                                      coerce_to_string=False)
