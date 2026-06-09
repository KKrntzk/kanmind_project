from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q
from board_app.models import Board
from .serializers import BoardSerializer
from .permissions import IsBoardOwnerOrMember

class BoardListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsBoardOwnerOrMember]

    def get(self, request):
        user = request.user
        boards = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = BoardSerializer(data=request.data)
        
        if serializer.is_valid():
            board = serializer.save(owner=request.user)

            return Response(BoardSerializer(board).data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
