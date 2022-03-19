from django.conf import settings
from rest_framework import authentication, exceptions, permissions


class WithBootstrapToken(permissions.BasePermission):
    token = settings.BOOTSTRAPTOKEN

    def has_permission(self, request, view):
        authorization = request.META.get('HTTP_AUTHORIZATION', '')
        # print(authentication)
        if not authorization:
            return False
        request_bootstrap_token = authorization.split()[-1]
        return self.token == request_bootstrap_token
