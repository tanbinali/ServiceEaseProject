from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from .models import Category, Service
from .serializers import CategorySerializer, ServiceSerializer
from common.permissions import IsAdminUser
from django.db.models import Avg, Prefetch


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('id').prefetch_related(
        Prefetch(
            'services',
            queryset=Service.objects.filter(active=True)
                .annotate(avg_rating=Avg('reviews__rating'))
                .order_by('id'),
            to_attr='prefetched_services'
        )
    )
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'services']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="List all categories",
        operation_description=(
            "Retrieve a list of all service categories. "
            "Accessible publicly without authentication."
        ),
        responses={200: CategorySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a specific category by ID",
        operation_description="Get detailed information about a specific category.",
        responses={200: CategorySerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new category",
        operation_description="Create a new category. Requires admin authentication.",
        request_body=CategorySerializer,
        responses={201: CategorySerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update an existing category (full update)",
        operation_description="Update all fields of a category. Requires admin authentication.",
        request_body=CategorySerializer,
        responses={200: CategorySerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial update of a category",
        operation_description="Update one or more fields of a category. Requires admin authentication.",
        request_body=CategorySerializer,
        responses={200: CategorySerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a category",
        operation_description="Delete a category by ID. Requires admin authentication.",
        responses={204: 'No Content'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="List active services under a category",
        operation_description=(
            "Retrieve all active services associated with the specified category. "
            "Returns 404 if no active services are found."
        ),
        responses={200: ServiceSerializer(many=True), 404: 'No active services found'}
    )
    @action(detail=True, methods=['get'])
    def services(self, request, pk=None):
        category = self.get_object()
        services = getattr(category, 'prefetched_services', [])
        if not services:
            return Response(
                {'detail': 'No active services found for this category.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'average_rating', 'active', 'duration']
    ordering = ['-average_rating']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        elif self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAuthenticated()]

    @swagger_auto_schema(
        operation_summary="List all services",
        operation_description="Retrieve a list of all services with optional search and ordering. Publicly accessible.",
        responses={200: ServiceSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a specific service by ID",
        operation_description="Get detailed information about a specific service.",
        responses={200: ServiceSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new service",
        operation_description="Create a new service. Requires admin authentication.",
        request_body=ServiceSerializer,
        responses={201: ServiceSerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a service (full update)",
        operation_description="Update all fields of an existing service. Requires admin authentication.",
        request_body=ServiceSerializer,
        responses={200: ServiceSerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial update a service",
        operation_description="Update one or more fields of a service. Requires admin authentication.",
        request_body=ServiceSerializer,
        responses={200: ServiceSerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a service",
        operation_description="Delete a service by ID. Requires admin authentication.",
        responses={204: 'No Content'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Service.objects.none()
        category_pk = self.kwargs.get('category_pk')
        qs = Service.objects.select_related('category').annotate(
            average_rating=Avg('reviews__rating')
        )
        if category_pk:
            qs = qs.filter(category_id=category_pk, active=True)
        return qs.order_by('-average_rating', 'id')
