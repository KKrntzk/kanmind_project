from django.contrib.auth.models import User
from rest_framework import serializers

from board_app.models import Board

class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer to handle board overview lists and board creation.
    Provides calculated metadata aggregates regarding task progression and priority
    directly alongside core board properties.
    """
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    member_count = serializers.SerializerMethodField()
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), write_only=True, required=False)
    
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

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
        """
        Count and return the total number of users registered as members of this board.
        """
        return obj.members.count() 
    
    def get_ticket_count(self, obj):
        """
        Count and return the total number of tasks associated with this board.
        """
        from task_app.models import Task
        return Task.objects.filter(board=obj).count()

    def get_tasks_to_do_count(self, obj):
        """
        Count and return the total number of tasks on this board currently in 'to-do' status.
        """
        from task_app.models import Task
        return Task.objects.filter(board=obj, status='to-do').count() 

    def get_tasks_high_prio_count(self, obj):
        """
        Count and return the total number of tasks on this board classified as 'high' priority.
        """
        from task_app.models import Task
        return Task.objects.filter(board=obj, priority='high').count()
    
    def create(self, validated_data):
        """
        Create a new board instance and establish membership relations.
        Extracts member data, instantiates the board, and ensures that the board's owner
        is automatically and non-negotiably included in the members relationship.
        """
        members_data = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)
        board.members.add(board.owner)
        
        if members_data:
            board.members.add(*members_data)
            
        return board
                

class BoardUserSerializer(serializers.ModelSerializer):
    """
    Lightweight user serializer specialized for nesting within board context payloads.
    Provides basic identity attributes including mapping the first_name field to fullname.
    """
    fullname = serializers.CharField(source='first_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']


class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Detailed read-only representation of a single board instance.
    Fully nests complex relations, exposing full member profiles and an array 
    of all assigned tasks attached to the board.
    """
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = BoardUserSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']

    def get_tasks(self, obj):
        """
        Fetch, serialize, and return all tasks linked to this board instance using AssignedTaskSerializer.
        """
        from task_app.api.serializers import AssignedTaskSerializer
        from task_app.models import Task

        board_tasks = Task.objects.filter(board=obj)
        return AssignedTaskSerializer(board_tasks, many=True).data
    

class BoardPATCHSerializer(serializers.ModelSerializer):
    """
    Serializer dedicated to handling partial updates (PATCH) on an existing board.
    Maintains a separation between write-only raw primary key lists for updating memberships
    and read-only nested objects for clean, informative response schemas.
    """
    owner_data = BoardUserSerializer(source='owner', read_only=True)
    members_data = BoardUserSerializer(source='members', many=True, read_only=True)
    
    members = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=User.objects.all(), 
        write_only=True, 
        required=False
    )

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data', 'members']

    def update(self, instance, validated_data):
        """
        Update the board's fields and re-evaluate membership state.
        Updates the title if provided and overrides the membership relation while safely 
        ensuring the board owner remains part of the board's user collective.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.save()

        if 'members' in validated_data:
            new_members = validated_data['members']
            if instance.owner not in new_members:
                new_members.append(instance.owner)
            instance.members.set(new_members)

        return instance