from django.urls import path
from .views import AssignedToMeTaskListView, ReviewingTaskListView, TaskCreateView, TaskDetailView

urlpatterns = [
    path('tasks/assigned-to-me/', AssignedToMeTaskListView.as_view(), name='tasks-assigned-to-me'),
    path('tasks/reviewing/', ReviewingTaskListView.as_view(), name='tasks-reviewing'),
    path('tasks/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:id>/', TaskDetailView.as_view(), name='task-detail'),
]