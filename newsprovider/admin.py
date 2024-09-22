from django.contrib import admin
from .models import ExternalArticleID, NewsCard, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Columns to display in the list view
    search_fields = ('name',)  # Fields to search by

@admin.register(NewsCard)
class NewsCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'summary', 'link', 'image')  # Columns to display in the list view
    search_fields = ('title', 'summary', 'link')  # Fields to search by
    list_filter = ('categories',)  # Filter by categories
    filter_horizontal = ('categories',)  # Add a horizontal filter widget for many-to-many fields

@admin.register(ExternalArticleID)
class ExternalIDAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'news_card_id', 'news_card__title')  # Change to correct field name

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('news_card')  # Prefetch related news_card

    # If you need to access the news_card ID directly, define a method
    # def news_card_id(self, obj):
    #     return obj.news_card.id if obj.news_card else None
    # news_card_id.short_description = 'News Card ID'