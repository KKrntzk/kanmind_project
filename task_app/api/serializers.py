from django.contrib.auth.models import User
from django.http import Http404
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from board_app.api.serializers import BoardUserSerializer
from board_app.models import Board
from task_app.models import Comment, Task


class AssignedTaskSerializer(serializers.ModelSerializer):
    """
    Serializer to represent tasks assigned to or reviewed by a specific user.
    Nests the BoardUserSerializer to output full assignee and reviewer profiles
    instead of plain database IDs.
    """

    assignee = BoardUserSerializer(read_only=True)
    reviewer = BoardUserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Serializer optimized for task creation.
    Accepts raw IDs via write-only fields (`assignee_id`, `reviewer_id`) to link relations,
    but returns fully nested object details in the response for frontend efficiency.
    """

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assignee",
        write_only=True,
        required=False,
        allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="reviewer",
        write_only=True,
        required=False,
        allow_null=True,
    )

    assignee = BoardUserSerializer(read_only=True)
    reviewer = BoardUserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "reviewer_id",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]
        read_only_fields = ["comments_count"]

    def to_internal_value(self, data):
        """
        Interceptors raw input data before Django REST Framework's standard field validation.
        Explicitly validates the existence of the target board in the database using the
        provided 'board' ID. If the board does not exist, it instantly raises an HTTP 404
        exception, preventing DRF from defaulting to a standard 400 Bad Request validation error.
        """

        board_id = data.get("board")
        if board_id is not None:
            try:
                Board.objects.get(id=board_id)
            except Board.DoesNotExist:
                raise Http404("this board does not exist")

        return super().to_internal_value(data)

    def validate(self, attrs):
        """
        Perform multi-field security and consistency checks before task creation.
        Ensures that the requesting creator, the selected assignee, and the assigned reviewer
        are legitimate members or the owner of the target board.
        """
        board = attrs.get("board")
        request_user = self.context["request"].user

        if request_user != board.owner and request_user not in board.members.all():
            raise PermissionDenied(
                "You have to be the owner or a member to the board, to add tasks to it"
            )

        assignee = attrs.get("assignee")
        if assignee and assignee != board.owner and assignee not in board.members.all():
            raise serializers.ValidationError(
                {"assignee_id": "You are not a member of the board"}
            )

        reviewer = attrs.get("reviewer")
        if reviewer and reviewer != board.owner and reviewer not in board.members.all():
            raise serializers.ValidationError(
                {"reviewer_id": "your reviewer is not a member of this board"}
            )

        return attrs


class TaskPatchSerializer(serializers.ModelSerializer):
    """
    Serializer specialized in handling partial updates (PATCH) on an existing task.
    Supports reassigning users via raw IDs while enforcing strict safety boundaries
    such as preventing board-migration.
    """

    board = serializers.PrimaryKeyRelatedField(
        queryset=Board.objects.all(), write_only=True, required=False
    )

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assignee",
        write_only=True,
        required=False,
        allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="reviewer",
        write_only=True,
        required=False,
        allow_null=True,
    )

    assignee = BoardUserSerializer(read_only=True)
    reviewer = BoardUserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "reviewer_id",
            "assignee",
            "reviewer",
            "due_date",
        ]

    def validate(self, attrs):
        """
        Validate partial modifications for an existing task instance.
        Verifies that the task stays locked to its original board, and checks that updated
        assignees or reviewers are active participants of that specific board.
        """
        board = self.instance.board

        if "board" in attrs and attrs.get("board") != board:
            raise serializers.ValidationError(
                {"board": "Changing the board of an existing task is not allowed."}
            )

        if "assignee" in attrs:
            assignee = attrs.get("assignee")
            if assignee is not None:
                if assignee != board.owner and assignee not in board.members.all():
                    raise serializers.ValidationError(
                        {"assignee_id": "your assignee is not a member of this board"}
                    )

        if "reviewer" in attrs:
            reviewer = attrs.get("reviewer")
            if reviewer is not None:
                if reviewer != board.owner and reviewer not in board.members.all():
                    raise serializers.ValidationError(
                        {"reviewer_id": "your reviewer is not a member of this board"}
                    )

        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer to handle both retrieving and posting task comments.
    Guarantees that empty comments are rejected and resolves the dynamic author
    representation by checking for first/last name combinations.
    """

    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]
        extra_kwargs = {"content": {"required": True, "allow_blank": False}}

    def get_author(self, obj):
        """
        Dynamically compile the author's display name.
        Combines first and last name if available; otherwise falls back to the system username.
        """
        fullname = f"{obj.author.first_name} {obj.author.last_name}".strip()
        return fullname if fullname else obj.author.username
