from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the `Review` model.

    Purpose:
        - Handles serialization and deserialization of review data.
        - Used for both public review retrieval and authenticated review creation/update.

    Fields:
        - id (int): Unique identifier of the review (read-only).
        - service (int): ID of the related service being reviewed.
            * Read-only to prevent clients from changing the associated service.
            * Automatically set in the view based on URL parameter (`service_pk`).
        - user (str): String representation of the user who created the review.
            * Read-only to ensure authorship cannot be altered.
        - rating (int): Numeric rating for the service (e.g., 1-5).
        - text (str): The textual content of the review.
        - created_at (datetime): Timestamp of when the review was created (read-only).

    Read-only Behavior:
        - `user` is assigned automatically from the authenticated request user.
        - `service` is assigned automatically from the path parameter in the view.

    Example:
        >>> ReviewSerializer(data={"rating": 5, "text": "Excellent service!"})
        # On save, service and user will be set automatically from the request context.
    """

    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'service', 'user', 'rating', 'text', 'created_at']
        read_only_fields = ['user', 'service']
