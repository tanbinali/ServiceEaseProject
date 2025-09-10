from rest_framework import viewsets, permissions, status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from .models import Review
from .serializers import ReviewSerializer
from common.permissions import IsOwnerOrAdmin


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Review.objects.none()
        service_id = self.kwargs.get('service_pk')
        if not service_id:
            return Review.objects.none()
        return Review.objects.filter(service_id=service_id).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, service_id=self.kwargs.get('service_pk'))

    @swagger_auto_schema(
        operation_summary="List all reviews for a specific service",
        operation_description=(
            "Retrieve a list of all reviews associated with the specified service. "
            "Requires authentication. Reviews are ordered by creation date descending."
        ),
        responses={200: ReviewSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a specific review by ID",
        operation_description="Get detailed information of a review identified by its ID.",
        responses={
            200: ReviewSerializer(),
            404: 'Review not found'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new review for a service",
        operation_description=(
            "Submit a new review linked to the specified service. "
            "Authentication required. The review will be associated with the logged-in user."
        ),
        request_body=ReviewSerializer,
        responses={
            201: ReviewSerializer(),
            400: 'Validation error',
            403: 'Permission denied'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Fully update a review",
        operation_description="Replace all fields of an existing review. Requires permission.",
        request_body=ReviewSerializer,
        responses={
            200: ReviewSerializer(),
            400: 'Validation error',
            403: 'Permission denied'
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update a review",
        operation_description="Update one or more fields of a review. Requires permission.",
        request_body=ReviewSerializer,
        responses={
            200: ReviewSerializer(),
            400: 'Validation error',
            403: 'Permission denied'
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a review",
        operation_description="Remove a review by its ID. Requires permission.",
        responses={
            204: 'Review deleted',
            403: 'Permission denied'
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class AllReviewsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public read-only viewset for reviews.
    Only admin can delete reviews.
    """
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]  # list & retrieve are public

    @swagger_auto_schema(
        operation_summary="List all reviews (public)",
        operation_description="Retrieve a list of all reviews across all services. No authentication required.",
        responses={200: ReviewSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a specific review by ID (public)",
        operation_description="Get detailed information of any review by ID without authentication.",
        responses={
            200: ReviewSerializer(),
            404: 'Review not found'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # Admin-only delete
    @swagger_auto_schema(
        operation_summary="Delete a review (admin only)",
        operation_description="Delete a specific review by ID. Admin authentication required.",
        responses={
            204: 'Review deleted successfully',
            403: 'Forbidden',
            404: 'Review not found'
        }
    )
    def destroy(self, request, *args, **kwargs):
        # Only allow admin
        if not request.user.is_staff:
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
