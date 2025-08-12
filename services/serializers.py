from rest_framework import serializers
from .models import Category, Service

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.

    Fields:
    - id: Unique identifier of the category.
    - name: Name of the category.
    - description: Description of the category.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class ServiceSerializer(serializers.ModelSerializer):
    """
    Serializer for Service model, including a read-only average rating field.

    Fields:
    - id: Unique identifier of the service.
    - name: Name of the service.
    - description: Description of the service.
    - category: Related category of the service.
    - price: Price of the service.
    - duration: Duration of the service.
    - image: Optional image representing the service.
    - active: Boolean indicating if the service is active.
    - created_at: Timestamp when the service was created.
    - updated_at: Timestamp when the service was last updated.
    - average_rating: Float value from the model's `avg_rating` property/method (read-only).
    """
    average_rating = serializers.FloatField(source='avg_rating', read_only=True)
    image = serializers.ImageField(
        required=False,)
    
    class Meta:
        model = Service
        fields = [
            'id', 'name', 'description', 'category', 'price', 'duration',
            'image', 'active', 'created_at', 'updated_at', 'average_rating'
        ]
