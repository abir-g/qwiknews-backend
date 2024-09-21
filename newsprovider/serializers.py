from rest_framework import serializers
from .models import NewsCard

class NewsCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsCard
        fields = ['title', 'summary', 'image', 'link']