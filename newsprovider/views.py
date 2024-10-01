from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework import mixins
from rest_framework import viewsets

from .serializers import NewsCardSerializer
from .models import NewsCard
from .pagination import DefaultPagination
# Create your views here.


class NewsCardViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    serializer_class = NewsCardSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        queryset = NewsCard.objects.filter(is_flagged=0).order_by('-timestamp')

        # Get the category_id and title search parameter from the URL query parameters
        category_id = self.kwargs.get('category_id')
        title_search = self.request.query_params.get('title', None)

        # Filter by category if provided
        if category_id:
            queryset = queryset.filter(categories__id=category_id)

        # Filter by title search if provided
        if title_search:
            queryset = queryset.filter(title__icontains=title_search)

        return queryset