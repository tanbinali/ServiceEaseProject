from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from .models import User, Profile
from .serializers import UserSerializer, ProfileSerializer, UserCreateSerializer
from common.permissions import IsAdminUser, IsOwnerOrAdmin


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related('profile').prefetch_related('groups').order_by('id')
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_permissions(self):
        if getattr(self, 'swagger_fake_view', False):
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'profile':
            return ProfileSerializer
        return UserSerializer

    @swagger_auto_schema(
        operation_summary="List all users",
        operation_description=(
            "Retrieve a paginated list of all users in the system. "
            "Only accessible by admin users."
        ),
        responses={200: UserSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a user by ID",
        operation_description=(
            "Fetch detailed information about a user specified by their ID. "
            "Includes related profile and group information."
        ),
        responses={200: UserSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new user",
        operation_description=(
            "Create a new user account. The request body must include required fields "
            "such as username, email, password, and any other mandatory fields."
        ),
        request_body=UserCreateSerializer,
        responses={201: UserSerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a user (full update)",
        operation_description=(
            "Update all fields of an existing user. The request must include "
            "all required fields, otherwise validation will fail."
        ),
        request_body=UserSerializer,
        responses={200: UserSerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update a user",
        operation_description=(
            "Update one or more fields of an existing user. "
            "Only the provided fields will be updated."
        ),
        request_body=UserSerializer,
        responses={200: UserSerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a user",
        operation_description="Delete a user by their ID. This action is irreversible.",
        responses={204: 'No Content'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        method='get',
        operation_summary="Retrieve a user's profile",
        operation_description=(
            "Get the profile information associated with a specific user. "
            "Accessible only by the user themselves or admin users."
        ),
        responses={200: ProfileSerializer()}
    )
    @swagger_auto_schema(
        method='put',
        operation_summary="Update a user's profile (full update)",
        operation_description=(
            "Fully update a user's profile. The request body must contain all fields."
        ),
        request_body=ProfileSerializer,
        responses={200: ProfileSerializer()}
    )
    @swagger_auto_schema(
        method='patch',
        operation_summary="Partially update a user's profile",
        operation_description=(
            "Partially update one or more fields of a user's profile."
        ),
        request_body=ProfileSerializer,
        responses={200: ProfileSerializer()}
    )
    @swagger_auto_schema(
        method='delete',
        operation_summary="Delete a user's profile",
        operation_description=(
            "Delete the profile of the specified user. This action cannot be undone."
        ),
        responses={204: 'No Content'}
    )
    @action(
        detail=True,
        methods=['get', 'put', 'patch', 'delete'],
        permission_classes=[IsAuthenticated, IsOwnerOrAdmin],
        serializer_class=ProfileSerializer
    )
    def profile(self, request, pk=None):
        user = self.get_object()
        profile = getattr(user, 'profile', None)
        if not profile:
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)

        elif request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(profile, data=request.data, partial=(request.method == 'PATCH'))
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        elif request.method == 'DELETE':
            profile.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class MyProfileViewSet(mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.select_related('user')

    def get_object(self):
        if getattr(self, 'swagger_fake_view', False):
            return None
        return get_object_or_404(Profile.objects.select_related('user'), user=self.request.user)

    @swagger_auto_schema(
        operation_summary="Retrieve my profile",
        operation_description="Get profile details of the currently authenticated user.",
        responses={200: ProfileSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update my profile (full update)",
        operation_description=(
            "Update all fields of the authenticated user's profile. "
            "Request body must include all required profile fields."
        ),
        request_body=ProfileSerializer,
        responses={200: ProfileSerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update my profile",
        operation_description=(
            "Partially update one or more fields of the authenticated user's profile."
        ),
        request_body=ProfileSerializer,
        responses={200: ProfileSerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
