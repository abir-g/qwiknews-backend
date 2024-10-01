from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NewsCardViewSet

# Create a router and register our viewset with it.
router = DefaultRouter()
router.register(r'newscards', NewsCardViewSet, basename='newscards')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),  # Include the router URLs
    path('category/<int:category_id>/', NewsCardViewSet.as_view({'get': 'list'}), name='news-by-category'),
]