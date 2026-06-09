from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q
from board_app.models import Board
from .serializers import BoardSerializer
from .permissions import IsBoardOwnerOrMember

class BoardListView(generics.ListCreateAPIView):

    serializer_class = BoardSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsBoardOwnerOrMember]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)