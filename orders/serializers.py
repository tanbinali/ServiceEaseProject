from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from django.contrib.auth import get_user_model
from datetime import timedelta
from common.permissions import is_user_admin
from django.db.models import Prefetch

User = get_user_model()


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'service', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if is_user_admin(request):
                self.fields['cart'].queryset = Cart.objects.all()
            else:
                self.fields['cart'].queryset = Cart.objects.filter(user=request.user)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_duration = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price', 'total_duration']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and not is_user_admin(request):
            self.fields['user'].queryset = User.objects.filter(id=request.user.id)

    def get_total_price(self, obj):
        items = getattr(obj, 'items', None)
        if items is None:
            return 0
        if hasattr(items, 'all'):
            items = items.all()
        return round(sum(item.service.price * item.quantity for item in items), 2)

    def get_total_duration(self, obj):
        total_duration = timedelta()
        items = getattr(obj, 'items', None)
        if items is None:
            return str(total_duration)
        if hasattr(items, 'all'):
            items = items.all()
        for item in items:
            total_duration += item.service.duration * item.quantity
        return str(total_duration)


class OrderItemSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)
    price = serializers.DecimalField(source="service.price", max_digits=10, decimal_places=2, read_only=True)
    duration = serializers.DurationField(source="service.duration", read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'service', 'service_name', 'price', 'duration', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    client = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    status = serializers.CharField(read_only=False)
    
    class Meta:
        model = Order
        fields = ['id', 'client', 'order_items', 'total_price', 'status', 'created_at', 'updated_at']
        read_only_fields = ['total_price', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if not is_user_admin(request):
                self.fields['client'].read_only = True
                self.fields['status'].read_only = True
            else:
                self.fields['client'].queryset = User.objects.all()
                self.fields['client'].read_only = False
                self.fields['status'].read_only = False

    def create(self, validated_data):
        request = self.context['request']
        user = request.user

        if is_user_admin(request):
            client = validated_data.get('client')
            if not client:
                raise serializers.ValidationError({"client": "Client is required for admin orders."})
        else:
            client = user

        try:
            cart = Cart.objects.prefetch_related(
                Prefetch('items', queryset=CartItem.objects.select_related('service'))
            ).get(user=client)
        except Cart.DoesNotExist:
            raise serializers.ValidationError({"cart": "No cart found for this user."})

        cart_items = cart.items.all()
        if not cart_items.exists():
            raise serializers.ValidationError({"cart": "No items in cart to place an order."})

        order = Order.objects.create(client=client)
        total_price = 0
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                service=item.service,
                quantity=item.quantity
            )
            total_price += item.service.price * item.quantity

        order.total_price = total_price
        order.save()

        cart.delete()
        return order

    def update(self, instance, validated_data):
        request = self.context['request']
        if not is_user_admin(request):
            validated_data.pop('status', None)
        return super().update(instance, validated_data)
