from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Board(models.Model):
    """
    Represents a collaborative Kanban board instance.
    Tracks the board's title, creation date, and manages user roles by establishing
    a single-user owner relationship and a multi-user team membership.
    """

    title = models.CharField(max_length=255)

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_boards"
    )

    members = models.ManyToManyField(User, related_name="joined_boards", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Return the string representation of the board, which is its title.
        """
        return self.title
