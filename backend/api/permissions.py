from rest_framework.permissions import BasePermission, SAFE_METHODS


class AuthorOrIsAuthenticatedPermission(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or (request.user == obj.author)
