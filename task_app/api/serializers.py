from rest_framework import serializers
from task_app.models import Task
from board_app.api.serializers import BoardUserSerializer

class AssignedTaskSerializer(serializers.ModelSerializer):
    assignee = BoardUserSerializer(read_only=True)
    reviewer = BoardUserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'board',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'reviewer',
            'due_date',
            'comments_count'
        ]