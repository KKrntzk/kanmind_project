from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from task_app.models import Task, Comment

from .serializers import AssignedTaskSerializer, TaskCreateSerializer, TaskPatchSerializer, CommentSerializer
from .permissions import IsTaskFieldsAllowed, IsBoardMemberForTaskUrl

class AssignedToMeTaskListView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AssignedTaskSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(assignee=user)
    

class ReviewingTaskListView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AssignedTaskSerializer  

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(reviewer=user)
    

class TaskCreateView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskCreateSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTaskFieldsAllowed]
    queryset = Task.objects.all()
    serializer_class = TaskPatchSerializer
    lookup_field = 'id'


class TaskCommentListView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsBoardMemberForTaskUrl]
    serializer_class = CommentSerializer

    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        get_object_or_404(Task, id=task_id)
        return Comment.objects.filter(task_id=task_id)

    def perform_create(self, serializer):
        task_id = self.kwargs.get('task_id')
        task = get_object_or_404(Task, id=task_id)
        
        serializer.save(author=self.request.user, task=task)