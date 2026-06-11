from django.urls import path
from .views import AssignedToMeTaskListView, ReviewingTaskListView, TaskCreateView, TaskDetailPatchView, TaskDetailDeleteView

urlpatterns = [
    path('tasks/assigned-to-me/', AssignedToMeTaskListView.as_view(), name='tasks-assigned-to-me'),
    path('tasks/reviewing/', ReviewingTaskListView.as_view(), name='tasks-reviewing'),
    path('tasks/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:id>/', TaskDetailPatchView.as_view(), name='task-detail-patch'),
    path('tasks/<int:id>/delete/', TaskDetailDeleteView.as_view(), name='task-delete'),
]