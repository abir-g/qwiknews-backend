from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class NewsCard(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    summary = models.TextField()
    image = models.ImageField(upload_to='news_images/')
    link = models.URLField(max_length=500)
    is_summarized = models.BooleanField(default=False)
    categories = models.ManyToManyField(Category, related_name='newscards')  # Many-to-many relationship
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class AppUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return f"{self.user.username}"