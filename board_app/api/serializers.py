from rest_framework import serializers
from board_app.models import Board
from django.contrib.auth.models import User

class BoardSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    member_count = serializers.SerializerMethodField()
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), write_only=True, required=False)
    
    ticket_count = serializers.IntegerField(default=0, read_only=True)
    tasks_to_do_count = serializers.IntegerField(default=0, read_only=True)
    tasks_high_prio_count = serializers.IntegerField(default=0, read_only=True)

    class Meta:
        model = Board
        fields = [
            'id', 
            'title', 
            'members',
            'member_count', 
            'ticket_count', 
            'tasks_to_do_count', 
            'tasks_high_prio_count', 
            'owner_id'
        ]

    def get_member_count(self, obj):
        return obj.members.count() 
    
    def create(self, validated_data):
        members_data = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)
        
        if members_data:
            board.members.set(members_data)
            
        return board
    

    
class BoardUserSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source='first_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']


class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = BoardUserSerializer(many=True, read_only=True)
    
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'owner_id',
            'members',
            'tasks'
        ]

    def get_tasks(self, obj):
        return []