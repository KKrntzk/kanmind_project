from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer to handle user registration requests.
    Validates input data, checks for password agreement, ensures email uniqueness,
    and returns the created user instance along with an authentication token.
    """

    fullname = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    token = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = User
        fields = [
            "fullname",
            "email",
            "password",
            "repeated_password",
            "token",
            "user_id",
        ]

    def validate(self, data):
        """
        Perform cross-field validation for registration.
        Verifies that the repeated password matches the original password
        and checks if the provided email address is already registered.
        """

        if data["password"] != data["repeated_password"]:
            raise ValidationError(
                {
                    "repeated_password": "your repeated password does not match your password"
                }
            )

        if User.objects.filter(email=data["email"]).exists():
            raise ValidationError({"email": "your email seems to be used already"})

        return data

    def create(self, validated_data):
        """
        Create a new active User instance and generate an authentication token.
        Maps the email to the username field, assigns the fullname to first_name,
        and attaches the freshly generated token key to the user object before returning it.
        """

        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["fullname"].strip(),
        )

        token = Token.objects.create(user=user)
        user.token = token.key

        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer to handle and validate user authentication credentials.
    Verifies that credentials are provided and match an active user account.
    """

    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Authenticate the user credentials using email and password.
        Validates that both fields are present, checks them against the database,
        and ensures the account is currently active before attaching the user instance to the validated data.
        """
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(username=email, password=password)

            if not user:
                raise ValidationError(
                    {"non_field_errors": "your email or password is not valid"}
                )

            if not user.is_active:
                raise ValidationError({"non_field_errors": "this account is inactive"})

        else:
            raise ValidationError(
                {"non_field_errors": "email and password has to be filled out"}
            )

        data["user"] = user
        return data
