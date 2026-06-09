from rest_framework import serializers
from board_app.models import Board

class BoardSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    member_count = serializers.SerializerMethodField()
    
    ticket_count = serializers.IntegerField(default=0, read_only=True)
    tasks_to_do_count = serializers.IntegerField(default=0, read_only=True)
    tasks_high_prio_count = serializers.IntegerField(default=0, read_only=True)

    class Meta:
        model = Board
        fields = [
            'id', 
            'title', 
            'member_count', 
            'ticket_count', 
            'tasks_to_do_count', 
            'tasks_high_prio_count', 
            'owner_id'
        ]

    def get_member_count(self, obj):
        return obj.members.count()