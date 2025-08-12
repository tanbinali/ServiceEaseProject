from rest_framework import serializers
from .models import User, Profile


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Profile model.

    Fields:
        - id (int): Unique identifier of the profile (read-only).
        - full_name (str): Full name of the user.
        - phone_number (str): Contact phone number.
        - address (str): Residential address.
        - profile_picture (image): Optional profile image.
        - bio (str): Short biography or description.
        - date_of_birth (date): User's date of birth.

    Usage:
        - Nested within UserSerializer.
        - Directly for profile CRUD operations.
    """
    profile_picture = serializers.ImageField(required=False)
    
    class Meta:
        model = Profile
        fields = ['id', 'full_name', 'phone_number', 'address', 'profile_picture', 'bio', 'date_of_birth']
        read_only_fields = ['id']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model with nested profile details.

    Fields:
        - id (int): Unique identifier of the user.
        - email (str): User's email address.
        - username (str): Username chosen by the user.
        - profile (ProfileSerializer): Nested profile information (read-only).
    """
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'profile']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new User.

    Fields:
        - id (int): Unique identifier (read-only).
        - email (str): Email address.
        - username (str): Username.
        - password (str): Write-only password field.

    Behavior:
        - Uses `create_user` to hash passwords before saving.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password']

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
