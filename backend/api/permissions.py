from rest_framework import permissions

class IsSelf(permissions.BasePermission):
    """
    Allows access only to the user sending request.
    """

    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id