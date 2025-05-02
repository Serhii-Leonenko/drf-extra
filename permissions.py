from django.conf import settings
from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class HasServiceToken(BasePermission):
    """
    Permission class for checking if the request has a valid service token.
    """

    def has_permission(self, request, view):
        token = request.headers.get("X-Service-Token")

        return bool(token and token == settings.INTERNAL_API_TOKEN)
