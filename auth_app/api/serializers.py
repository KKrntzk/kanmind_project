from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token

class RegistrationSerializer(serializers.ModelSerializer):


    fullname = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    token = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password', 'token', 'user_id']

    def validate(self, data):

        if data['password'] != data['repeated_password']:
            raise ValidationError({'repeated_password':'your repeated password does not match your password'})
        
        if User.objects.filter(email=data['email']).exists():
            raise ValidationError({'email':'your email seems to be used already'})
        
        return data
    
    def create(self, validated_data):

        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['fullname'].strip()
        )

        token= Token.objects.create(user=user)
        user.token = token.key

        return user
