from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework import mixins
from rest_framework import viewsets

from .serializers import NewsCardSerializer
from .models import NewsCard
from .pagination import DefaultPagination
# Create your views here.


class NewsCardViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = NewsCard.objects.all()
    serializer_class = NewsCardSerializer
    pagination_class = DefaultPagination