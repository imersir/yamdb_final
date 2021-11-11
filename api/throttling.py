from rest_framework.throttling import ScopedRateThrottle

from .models import User

EMPLOYEES = (User.ADMIN_ROLE, User.MODERATOR_ROLE)


class NonEmployeeScopedRateThrottle(ScopedRateThrottle):

    def get_cache_key(self, request, view):
        if request.user.is_authenticated and request.user.role in EMPLOYEES:
            return None
        return super().get_cache_key(request, view)
