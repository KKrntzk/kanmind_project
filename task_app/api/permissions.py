from rest_framework.permissions import BasePermission
from board_app.api.permissions import IsBoardOwnerOrMember, IsBoardOwnerOnly

class IsBoardMemberForTask(IsBoardOwnerOrMember):
    message = "Permissions required: you have to be a member to get access to the task"

    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj.board)


class IsTaskCreatorOrBoardOwner(BasePermission):
    message = "Permissions required: Only the task creator or board owner can delete this task."

    def has_object_permission(self, request, view, obj):
        user = request.user
        board = obj.board
        
        is_board_owner = (user == board.owner)
        
        is_task_creator = hasattr(obj, 'creator') and (user == obj.creator)
        
        return is_board_owner or is_task_creator