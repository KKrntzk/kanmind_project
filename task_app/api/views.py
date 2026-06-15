from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from task_app.models import Task, Comment

from .serializers import AssignedTaskSerializer, TaskCreateSerializer, TaskPatchSerializer, CommentSerializer
from .permissions import IsTaskFieldsAllowed, IsBoardMemberForTaskUrl, IsCommentAuthorOnly

class AssignedToMeTaskListView(generics.ListAPIView):
    """
    API endpoint that lists all tasks assigned to the currently authenticated user.
    Uses TokenAuthentication to identify the user and filter tasks accordingly.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AssignedTaskSerializer

    def get_queryset(self):
        """
        Filter and return tasks where the active user is set as the assignee.
        """
        user = self.request.user
        return Task.objects.filter(assignee=user)
    

class ReviewingTaskListView(generics.ListAPIView):
    """
    API endpoint that lists all tasks where the authenticated user is registered as a reviewer.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AssignedTaskSerializer  

    def get_queryset(self):
        """
        Filter and return tasks where the active user is set as the reviewer.
        """
        user = self.request.user
        return Task.objects.filter(reviewer=user)
    

class TaskCreateView(generics.CreateAPIView):
    """
    API endpoint to create a new task.
    Requires authentication and automatically binds the creating user to the task instance.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskCreateSerializer

    def perform_create(self, serializer):
        """
        Save the task instance while enforcing the authenticated user as the task's creator.
        """
        serializer.save(creator=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update (PATCH), or delete a specific task by its ID.
    Integrates custom object-level permissions to safeguard modifications and destructive actions.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTaskFieldsAllowed]
    queryset = Task.objects.all()
    serializer_class = TaskPatchSerializer
    lookup_field = 'id'


class TaskCommentListView(generics.ListCreateAPIView):
    """
    API endpoint to handle both listing and creating comments for a specific task.
    Enforces board-level membership validation via URL parameters before accessing or adding comments.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsBoardMemberForTaskUrl]
    serializer_class = CommentSerializer

    def get_queryset(self):
        """
        Verify the existence of the task and return its related comments.
        Triggers a 404 response if the task does not exist.
        """
        task_id = self.kwargs.get('task_id')
        get_object_or_404(Task, id=task_id)
        return Comment.objects.filter(task_id=task_id)

    def perform_create(self, serializer):
        """
        Save the new comment, explicitly linking it to the target task and the authenticated author.
        """
        task_id = self.kwargs.get('task_id')
        task = get_object_or_404(Task, id=task_id)
        
        serializer.save(author=self.request.user, task=task)

class CommentDeleteView(generics.DestroyAPIView):
    """
    API endpoint to delete a specific comment from a specific task.
    Ensures data consistency and strictly limits the deletion to the original author of the comment.
    """
    authentication_classes = [TokenAuthentication]

    permission_classes = [IsAuthenticated, IsCommentAuthorOnly]
    serializer_class = CommentSerializer

    def get_object(self):
        """
        Fetch the comment ensuring it belongs to the specified task.
        Validates the existence of both entities and triggers object-level permission checks.
        """
        task_id = self.kwargs.get('task_id')
        comment_id = self.kwargs.get('comment_id')
        
        get_object_or_404(Task, id=task_id)
        comment = get_object_or_404(Comment, id=comment_id, task_id=task_id)
        
        self.check_object_permissions(self.request, comment)
        
        return comment