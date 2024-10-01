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
    queryset = NewsCard.objects.filter(is_flagged=0)
    serializer_class = NewsCardSerializer
    pagination_class = DefaultPagination