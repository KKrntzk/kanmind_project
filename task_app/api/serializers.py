from rest_framework import serializers
from task_app.models import Task
from board_app.api.serializers import BoardUserSerializer
from board_app.models import Board
from django.contrib.auth.models import User

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

class TaskCreateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assignee', write_only=True, required=False, allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='reviewer', write_only=True, required=False, allow_null=True
    )
    
    assignee = BoardUserSerializer(read_only=True)
    reviewer = BoardUserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'assignee_id', 'reviewer_id', 'assignee', 'reviewer', 'due_date', 'comments_count'
        ]
        read_only_fields = ['comments_count']


    def validate(self, attrs):
        board = attrs.get('board')
        request_user = self.context['request'].user

    
        if request_user != board.owner and request_user not in board.members.all():
            raise serializers.ValidationError(
                {"detail": "You have to be the owner or a member to the board, to add tasks to it"}
            )

    
        assignee = attrs.get('assignee')
        if assignee and assignee != board.owner and assignee not in board.members.all():
            raise serializers.ValidationError(
                {"assignee_id": "You are not a member of the board"}
            )

        reviewer = attrs.get('reviewer')
        if reviewer and reviewer != board.owner and reviewer not in board.members.all():
            raise serializers.ValidationError(
                {"reviewer_id": "your reviewer is not a member of this board"}
            )

        return attrs