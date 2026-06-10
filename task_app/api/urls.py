from django.urls import path
from .views import AssignedToMeTaskListView

urlpatterns = [
    path('tasks/assigned-to-me/', AssignedToMeTaskListView.as_view(), name='tasks-assigned-to-me'),
]