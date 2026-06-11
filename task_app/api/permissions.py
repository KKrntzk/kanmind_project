from rest_framework.permissions import BasePermission, SAFE_METHODS
from board_app.api.permissions import IsBoardOwnerOrMember, IsBoardOwnerOnly

class IsTaskFieldsAllowed(IsBoardOwnerOrMember):

    message = "Permissions required: You do not have the required permissions for this action."

    def has_object_permission(self, request, view, obj):
        user = request.user
        board = obj.board

        if request.method in SAFE_METHODS or request.method == 'PATCH':
            if not super().has_object_permission(request, view, board):
                self.message = "Permissions required: you have to be a member to get access to the task"
                return False
            return True

        if request.method == 'DELETE':
            is_board_owner = (user == board.owner)
            is_task_creator = hasattr(obj, 'creator') and (user == obj.creator)
            
            if not is_board_owner and not is_task_creator:
                self.message = "Permissions required: Only the task creator or board owner can delete this task."
                return False
            return True

        return False