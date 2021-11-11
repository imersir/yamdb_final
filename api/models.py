from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import (
    CharField, EmailField, TextField, UniqueConstraint
)

from .managers import APIUserManager


class User(AbstractUser):
    USER_ROLE = 'user'
    MODERATOR_ROLE = 'moderator'
    ADMIN_ROLE = 'admin'

    ROLES = (
        (USER_ROLE, 'пользователь'),
        (MODERATOR_ROLE, 'модератор'),
        (ADMIN_ROLE, 'админ')
    )
    username = CharField(
        'username',
        max_length=150,
        unique=True,
        null=True,
        help_text='Обязательное поле. Не более 150 символов, которые могу '
                  'состоять только из букв, цифр и знаков @/./+/-/_',
        validators=(AbstractUser.username_validator,),
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.',
        },
    )
    email = EmailField('Email', unique=True)
    role = CharField('Роль', default=USER_ROLE, max_length=30, choices=ROLES)
    bio = TextField('Биография', blank=True)

    objects = APIUserManager()

    class Meta(AbstractUser.Meta):
        ordering = ('id',)

    def __str__(self):
        return self.username if self.username else '~empty~'

    @property
    def is_user(self):
        return self.role == self.USER_ROLE

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR_ROLE

    @property
    def is_admin(self):
        return self.role == self.ADMIN_ROLE


class Review(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Автор отзыва'
    )
    title = models.ForeignKey(
        'Title', on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Отзыв')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации отзыва', auto_now_add=True
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=(MinValueValidator(1, 'Меньше 1 поставить нельзя'),
                    MaxValueValidator(10, 'Больше 10 поставить нельзя'))
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = (
            UniqueConstraint(
                name='reviews-unique-author',
                fields=('author', 'title')
            ),
        )

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор комментария')
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Отзыв')
    text = models.TextField(verbose_name='Текст комментария')
    pub_date = models.DateTimeField(verbose_name='Дата добавления комментария',
                                    auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]


class CategoryAndGenreBaseModel(models.Model):
    name = models.CharField(verbose_name='Название', max_length=200,
                            unique=True)
    slug = models.SlugField(verbose_name='URL', unique=True)

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(CategoryAndGenreBaseModel):
    class Meta(CategoryAndGenreBaseModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(CategoryAndGenreBaseModel):
    class Meta(CategoryAndGenreBaseModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(verbose_name='Название', max_length=200)
    year = models.PositiveSmallIntegerField(
        verbose_name='Год создания',
        blank=True, null=True,
        db_index=True
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        blank=True,
        related_name='titles'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name='Категория',
        related_name='titles'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name
