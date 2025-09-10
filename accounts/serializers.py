from rest_framework import serializers
from .models import User, Profile
from django.contrib.auth.models import Group
from rest_framework import serializers

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
    Serializer for the User model including nested profile information 
    and admin-restricted group modification.

    Fields:
        - id (int): User ID (read-only)
        - email (str): User's email
        - username (str): Username
        - profile (ProfileSerializer): Nested read-only profile information
        - groups (list[str]): List of group names. Editable only by admin users.

    Permissions:
        - Only admin users (is_staff=True) can modify the 'groups' field.
        - Other fields can be updated by authorized users as usual.
    """
    profile = ProfileSerializer(read_only=True)
    
    groups = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Group.objects.all(),
        required=False
    )

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'profile', 'groups']

    def update(self, instance, validated_data):
        """
        Update a user instance.

        Admin-only group update logic:
            - If 'groups' is in the request, check if the request user is admin.
            - If not admin, raise a ValidationError.
            - If admin, update the user's groups.

        Other fields are updated normally.
        """
        request = self.context.get('request')
        groups = validated_data.pop('groups', None)

        # Admin-only groups update
        if groups is not None:
            if not request.user.is_staff:
                raise serializers.ValidationError({
                    "groups": "You do not have permission to change user groups."
                })
            instance.groups.set(groups)

        # Update remaining fields
        return super().update(instance, validated_data)


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

