"""
URL routing configuration for the board management application.
Defines endpoints for listing and creating boards, retrieving or modifying 
specific board details, and validating user emails for invitations.
"""

from django.urls import path
from .views import BoardListView, BoardDetailView, EmailCheckView

urlpatterns = [
    path('boards/', BoardListView.as_view(), name='board-list'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
]