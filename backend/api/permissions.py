from rest_framework import permissions

class IsSelfOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # GET, HEAD or OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.id == request.user.id