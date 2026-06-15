from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import RegistrationSerializer, LoginSerializer
from rest_framework.authtoken.models import Token

class RegistrationView(APIView):
    """
    API endpoint that allows new users to register an account.
    Deactivates restriction checks to accept public registration requests,
    validates the user data, and returns user details alongside a fresh auth token.
    """
    
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle POST requests for user registration.
        Validates input data against the RegistrationSerializer. Returns a 201 response 
        with user details and token if valid, or a 400 response with errors if invalid.
        """

        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            response_data = {
                "token": user.token,
                "fullname": user.first_name,  
                "email": user.email,
                "user_id": user.id
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    """
    API endpoint that allows existing users to authenticate.
    Provides public access to verify credentials, checks active status,
    and returns an existing or newly generated authentication token upon success.
    """
    permission_classes=[AllowAny]

    def post(self,request):
        """
        Handle POST requests for user login.
        Validates credentials via LoginSerializer. Fetches or creates an auth token for the user,
        returning a 200 response with account data on success, or a 400 response on failure.
        """

        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            token, created = Token.objects.get_or_create(user=user)

            response_data = {
                "token": token.key,
                "fullname": user.first_name,  
                "email": user.email,
                "user_id": user.id
            }

            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)