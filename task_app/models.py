from django.db import models
from django.contrib.auth.models import User
from board_app.models import Board

# Create your models here.

class Task(models.Model):

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
        return f"{self.title} ({self.status})"