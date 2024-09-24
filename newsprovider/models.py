from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class NewsCard(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    summary = models.TextField(null=True, blank=True)
    # image = models.ImageField(upload_to='news_images/') #This will be used if the image data is being stored locally.
    image = models.URLField(max_length=600)
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
    
class ExternalArticleID(models.Model):
    external_id = models.IntegerField(unique=True)
    news_card = models.OneToOneField('NewsCard', on_delete=models.CASCADE, related_name='external_article_id', null=True)

    def __str__(self) -> str:
        return str(self.external_id)