from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from task_app.models import Task

from .serializers import AssignedTaskSerializer, TaskCreateSerializer, TaskPatchSerializer
from .permissions import IsBoardMemberForTask, IsTaskCreatorOrBoardOwner

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


class TaskDetailPatchView(generics.RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsBoardMemberForTask]
    queryset = Task.objects.all()
    serializer_class = TaskPatchSerializer
    lookup_field = 'id'
        

class TaskDetailDeleteView(generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTaskCreatorOrBoardOwner]
    queryset = Task.objects.all()
    lookup_field = 'id'