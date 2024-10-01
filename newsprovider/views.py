from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError


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
        
        # Get query parameters
        category_id = self.request.query_params.get('category_id')
        category_name = self.request.query_params.get('category_name')
        title_search = self.request.query_params.get('title_search')

        # Check if both parameters are provided
        if category_id and category_name:
            raise ValidationError("Please provide only one of 'category_id' or 'category_name', not both.")

        # Filter by category_id if provided
        if category_id:
            queryset = queryset.filter(categories__id=category_id)

        # Filter by category_name if provided
        if category_name:
            queryset = queryset.filter(categories__name__icontains=category_name)

        # Filter by title_search if provided
        if title_search:
            queryset = queryset.filter(title__icontains=title_search)

        return queryset
