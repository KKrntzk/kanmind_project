from rest_framework import permissions

class IsBoardOwnerOrMember(permissions.BasePermission):
    """
    Object-level permission to allow access only to the board's owner or its registered members.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or obj.members.filter(id=request.user.id).exists()
    

class IsBoardOwnerOnly(permissions.BasePermission):
    """
    Strict object-level permission that restricts all operations exclusively to the owner of the board.
    Denies access to any other user, including regular board members.
    """

    def has_object_permission(self, request, view, obj):
        """
        Verify if the authenticated user is strictly the designated owner of the target board object.
        """
        return obj.owner == request.user