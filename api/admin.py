from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Category, Comment, Genre, Review, Title, User


@admin.register(User)
class APIUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'role', 'first_name',
                    'last_name', 'bio', 'is_staff')
    list_display_links = ('id', 'username')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'bio')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('email', 'role', 'is_staff')}),
    )
    ordering = ('id',)


@admin.register(Review)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ('text', 'title', 'score', 'author', 'pub_date')
    list_filter = ('pub_date',)
    search_fields = ('text',)
    ordering = ('-pub_date',)


@admin.register(Comment)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ('text', 'review', 'author', 'pub_date')
    list_filter = ('pub_date',)
    search_fields = ('text',)
    ordering = ('-pub_date',)


@admin.register(Category)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('name',)


@admin.register(Genre)
class GenresAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('name',)


@admin.register(Title)
class TitlesAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'description', 'category')
    list_filter = ('category', 'genre')
    empty_value_display = '--нет--'
