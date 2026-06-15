from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework import permissions
from board_app.api.permissions import IsBoardOwnerOrMember, IsBoardOwnerOnly
from django.shortcuts import get_object_or_404
from task_app.models import Task

class IsTaskFieldsAllowed(IsBoardOwnerOrMember):
    """
    Custom permission to restrict actions on a Task instance.
    Inherits from IsBoardOwnerOrMember to leverage existing board-level membership checks.
    Allows safe operations (GET) and partial updates (PATCH) for all board members, 
    but restricts deletion (DELETE) strictly to the board owner or the original task creator.
    """

    message = "Permissions required: You do not have the required permissions for this action."

    def has_object_permission(self, request, view, obj):
        """
        Check if the requesting user has permission to perform the action on a specific Task.
        Dynamically adjusts the error message based on whether a membership check fails 
        or a deletion restriction is violated.
        """
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
    """
    Bridge permission used for endpoints where a task ID is provided in the URL path.
    Extracts the task, identifies its parent board, and delegates the permission evaluation 
    to the standard IsBoardOwnerOrMember class to ensure the user belongs to the board.
    """
    message = "Permissions required: You must be a member of the board to access this content."

    def has_permission(self, request, view):
        """
        Perform a high-level permission check based on the URL kwargs.
        Fetches the task by its ID, locates the associated board, and triggers object-level 
        permission checks against the board instance.
        """
        task_id = view.kwargs.get('task_id')
        task = get_object_or_404(Task, id=task_id)    
        board = task.board
        board_permission = IsBoardOwnerOrMember()
        
        return board_permission.has_object_permission(request, view, board)
    

class IsCommentAuthorOnly(permissions.BasePermission):
    """
    Object-level permission to restrict modifications on specific comment instances.
    Ensures that destructive actions (like deletion) are exclusively granted to the user 
    who originally authored the comment.
    """
    message = "Permissions required: Only the author of this comment is allowed to delete it."

    def has_object_permission(self, request, view, obj):
        """
        Verify that the requesting user matches the author of the target comment object.
        """
        return obj.author == request.user