from rest_framework import serializers
from board_app.models import Board
from django.contrib.auth.models import User

class BoardSerializer(serializers.ModelSerializer):
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
        return obj.members.count() 
    
    def get_ticket_count(self, obj):
        from task_app.models import Task
        return Task.objects.filter(board=obj).count()

    def get_tasks_to_do_count(self, obj):
        from task_app.models import Task
        return Task.objects.filter(board=obj, status='to-do').count() 

    def get_tasks_high_prio_count(self, obj):
        from task_app.models import Task
        return Task.objects.filter(board=obj, priority='high').count()
    
    def create(self, validated_data):
        members_data = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)
        board.members.add(board.owner)
        
        if members_data:
            board.members.add(*members_data)
            
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
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']

    def get_tasks(self, obj):
        from task_app.api.serializers import AssignedTaskSerializer
        from task_app.models import Task

        board_tasks = Task.objects.filter(board=obj)
        return AssignedTaskSerializer(board_tasks, many=True).data
    

class BoardPATCHSerializer(serializers.ModelSerializer):
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
        instance.title = validated_data.get('title', instance.title)
        instance.save()

        if 'members' in validated_data:
            new_members = validated_data['members']
            if instance.owner not in new_members:
                new_members.append(instance.owner)
            instance.members.set(new_members)

        return instance