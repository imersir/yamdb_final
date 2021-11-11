from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsStaffOrAuthorOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated or SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated
                and (request.user.is_moderator
                     or request.user.is_admin
                     or request.user == obj.author))


class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or (request.user.is_authenticated
                    and request.user.is_admin))


class HasUsernameForPOST(BasePermission):
    """
    Since the message has been rewritten, that permission should be placed
    last and joined with "&"(AND) or ","(comma) to display the correct
    matching answer.
    """
    message = ('Вы не можете оставлять отзывы и комментарии без '
               'предварительной установки параметра username через '
               'PATCH-запрос на адрес api/v1/users/me/')

    def has_permission(self, request, view):
        return request.method != 'POST' or request.user.username
