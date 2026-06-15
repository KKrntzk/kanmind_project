from django.db import models
from django.contrib.auth.models import User
from board_app.models import Board

# Create your models here.

class Task(models.Model):
    """
    Represents a single task item within a Kanban board.
    Tracks core attributes such as title, description, status, priority, due date,
    and handles relations to the respective board, creator, assignee, and reviewer.
    """

    class StatusChoices(models.TextChoices):
        TODO = 'to-do', 'To Do'
        IN_PROGRESS = 'in-progress', 'In Progress'
        REVIEW = 'review', 'Review'  
        DONE = 'done', 'Done'

    class PriorityChoices(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    
    
    status = models.CharField(
        max_length=20, 
        choices=StatusChoices.choices, 
        default=StatusChoices.TODO
    )
    priority = models.CharField(
        max_length=20, 
        choices=PriorityChoices.choices, 
        default=PriorityChoices.MEDIUM
    )
    
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_tasks')
    due_date = models.DateField(null=True, blank=True)
    comments_count = models.IntegerField(default=0)

    def __str__(self):
        """
        Return a string representation of the task, showing its title and status.
        """
        return f"{self.title} ({self.status})"
    



class Comment(models.Model):
    """
    Represents a text comment left by a user on a specific task.
    Includes automated timestamping upon creation and database-level chronological sorting.
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Meta options for the Comment model.
        Configures the default database ordering to be chronological by creation time.
        """
        ordering = ['created_at']

    def __str__(self):
        """
        Return a string representation stating the author's username and the target task ID.
        """
        return f"Comment by {self.author.username} on Task {self.task.id}"