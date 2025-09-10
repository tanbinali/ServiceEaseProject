from rest_framework import serializers
from .models import User, Profile

from rest_framework import serializers
from django.db.models import Prefetch
from services.models import Service

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    profile_picture = serializers.ImageField(required=False)
    service_history = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id', 'username', 'email',
            'full_name', 'phone_number', 'address',
            'profile_picture', 'bio', 'date_of_birth',
            'service_history'
        ]
        read_only_fields = ['id', 'username', 'email', 'service_history']

    def get_service_history(self, obj):
        orders = getattr(obj.user, 'orders', None)
        if orders is None:
            return []

        history = []
        for order in orders.all():
            services = []
            order_items = getattr(order, 'order_items', None)
            if order_items is not None:
                for item in order_items.all():
                    services.append({
                        "service_id": item.service.id,
                        "name": item.service.name,
                        "price": item.service.price,
                        "quantity": item.quantity,
                    })
            history.append({
                "order_id": order.id,
                "order_status": order.status,
                "total_price": order.total_price,
                "ordered_at": order.created_at,
                "services": services,
            })
        return history


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model with nested profile details and read-only groups.

    Fields:
        - id (int): Unique identifier of the user.
        - email (str): User's email address.
        - username (str): Username chosen by the user.
        - profile (ProfileSerializer): Nested profile information (read-only).
        - groups (list): List of user's group names (read-only).
    """
    profile = ProfileSerializer(read_only=True)
    groups = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'profile', 'groups']

    def get_groups(self, obj):
        return list(obj.groups.values_list('name', flat=True))


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
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
        )
        user.is_active = False  # disable login until email activation
        user.save()
        return user

