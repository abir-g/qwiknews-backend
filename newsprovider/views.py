from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet

from .serializers import NewsCardSerializer
from .models import NewsCard
from .pagination import DefaultPagination
# Create your views here.


class NewsCardViewSet(ReadOnlyModelViewSet):
    queryset = NewsCard.objects.all()
    serializer_class = NewsCardSerializer
    pagination_class = DefaultPagination