from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Newscard(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField()
    image = models.ImageField(upload_to='news_images/')
    link = models.URLField(max_length=500)
    categories = models.ManyToManyField(Category, related_name='newscards')  # Many-to-many relationship

    def __str__(self):
        return self.title
