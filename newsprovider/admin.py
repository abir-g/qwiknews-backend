from django.contrib import admin
from .models import Newscard, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Columns to display in the list view
    search_fields = ('name',)  # Fields to search by

@admin.register(Newscard)
class NewscardAdmin(admin.ModelAdmin):
    list_display = ('title', 'summary', 'link', 'image')  # Columns to display in the list view
    search_fields = ('title', 'summary', 'link')  # Fields to search by
    list_filter = ('categories',)  # Filter by categories
    filter_horizontal = ('categories',)  # Add a horizontal filter widget for many-to-many fields
