from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework import permissions
from board_app.api.permissions import IsBoardOwnerOrMember, IsBoardOwnerOnly
from django.shortcuts import get_object_or_404
from task_app.models import Task

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
    

class IsBoardMemberForTaskUrl(BasePermission):
    message = "Permissions required: You must be a member of the board to access this content."

    def has_permission(self, request, view):
        task_id = view.kwargs.get('task_id')
        task = get_object_or_404(Task, id=task_id)    
        board = task.board
        board_permission = IsBoardOwnerOrMember()
        
        return board_permission.has_object_permission(request, view, board)
    

class IsCommentAuthorOnly(permissions.BasePermission):
    message = "Permissions required: Only the author of this comment is allowed to delete it."

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user