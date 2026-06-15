from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from board_app.models import Board

from .permissions import IsBoardOwnerOnly, IsBoardOwnerOrMember
from .serializers import (BoardDetailSerializer, BoardPATCHSerializer, BoardSerializer, BoardUserSerializer,)

class BoardListView(generics.ListCreateAPIView):
    """
    API endpoint to list all boards associated with the user or create a new board.
    Enforces token authentication and limits access to authorized owners or members.
    """

    serializer_class = BoardSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsBoardOwnerOrMember]

    def get_queryset(self):
        """
        Retrieve a distinct list of boards where the current user is either the owner 
        or registered as a team member.
        """
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def perform_create(self, serializer):
        """
        Automatically assign the authenticated user as the owner of the newly created board.
        """
        serializer.save(owner=self.request.user)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a specific board instance.
    Dynamically swaps serializers depending on the action and tightens permission 
    restrictions for destructive requests.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsBoardOwnerOrMember]

    def get_queryset(self):
        """
        Scope database lookups to boards where the active user is a valid owner or member.
        """
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def get_serializer_class(self):
        """
        Return BoardPATCHSerializer for structural updates (PUT/PATCH) 
        and fall back to BoardDetailSerializer for standard read operations.
        """
        if self.request.method in ['PATCH', 'PUT']:
            return BoardPATCHSerializer
        return BoardDetailSerializer 
    
    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        Overrides the default list to ensure only the explicit board owner can execute a DELETE action.
        """
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsBoardOwnerOnly()]
        return super().get_permissions()
    

class EmailCheckView(APIView):
    """
    API view to verify if a given email address is linked to an existing user account.
    Primarily utilized by the frontend to safely search and validate members before adding them to a board.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Handle incoming GET requests to check email availability.
        Validates the presence and format of the 'email' query parameter, checks the database,
        and returns the user's basic profile data if matched, or error statuses if not.
        """
        email = request.query_params.get('email', None)

        if not email:
            return Response(
                {"detail": "This email is missing"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {"detail": "this is the wrong format"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            serializer = BoardUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {"detail": "email can't be matched to another user"}, 
                status=status.HTTP_404_NOT_FOUND
            )