from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Board(models.Model):
    title = models.CharField(max_length=255)
   
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_boards')    
    
    members = models.ManyToManyField(User, related_name='joined_boards', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return self.title