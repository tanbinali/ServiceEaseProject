from django.urls import path, include, re_path
from rest_framework_nested import routers
from django.conf import settings
from django.conf.urls.static import static
from common.views import redirect_from_base
from accounts.views import UserViewSet, ProfileViewSet
from services.views import CategoryViewSet, ServiceViewSet
from orders.views import CartViewSet, OrderViewSet, CartItemViewSet, OrderItemViewSet
from reviews.views import ReviewViewSet, AllReviewsViewSet
from django.contrib import admin
from debug_toolbar.toolbar import debug_toolbar_urls
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Schema view configuration for Swagger and Redoc API documentation
schema_view = get_schema_view(
   openapi.Info(
      title="Service Ease API",
      default_version='v1',
      description="API documentation for the Service Ease application.",
      terms_of_service="https://www.serviceease.com/terms/",
      contact=openapi.Contact(email="tanbinali@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# Main router for registering top-level viewsets
router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'services', ServiceViewSet, basename='services')
router.register(r'carts', CartViewSet, basename='carts')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'reviews', AllReviewsViewSet, basename='reviews')
router.register(r'profile', ProfileViewSet, basename='profile')

from rest_framework_nested.routers import NestedSimpleRouter

# Nested routes for user-related orders and reviews
users_router = NestedSimpleRouter(router, r'users', lookup='user')
users_router.register(r'orders', OrderViewSet, basename='user-orders')
users_router.register(r'reviews', ReviewViewSet, basename='user-reviews')

# Nested routes for category-related services
category_router = routers.NestedDefaultRouter(router, r'categories', lookup='category')
category_router.register(r'services', ServiceViewSet, basename='category-services')

# Nested routes for service-related reviews
service_router = routers.NestedDefaultRouter(router, r'services', lookup='service')
service_router.register(r'reviews', ReviewViewSet, basename='service-reviews')

# Nested routes for cart items under carts
cart_router = NestedSimpleRouter(router, r'carts', lookup='cart')
cart_router.register(r'items', CartItemViewSet, basename='cart-items')

# Nested routes for order items under orders
order_router = NestedSimpleRouter(router, r'orders', lookup='order')
order_router.register(r'items', OrderItemViewSet, basename='order-items')

urlpatterns = [
    # Admin site URL
    path('admin/', admin.site.urls),

    # Redirect root URL to a base landing page or another URL
    path('', redirect_from_base, name='redirect-from-base'),

    # Swagger/OpenAPI schema and UI endpoints
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

   # Authentication endpoints using Djoser (including JWT)
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    
    
    # API endpoints from the main and nested routers
    path('api/', include(router.urls)),
    path('api/', include(users_router.urls)),
    path('api/', include(category_router.urls)),
    path('api/', include(service_router.urls)),
    path('api/', include(cart_router.urls)),
    path('api/', include(order_router.urls)),
] + debug_toolbar_urls()

my_profile = ProfileViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update'
})

urlpatterns += [
    path('api/profile/me/', my_profile, name='my-profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
