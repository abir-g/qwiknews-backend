import os
import requests
from django.utils import timezone
from django.db import transaction
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qwiknews.settings')
django.setup()

from newsprovider.models import ExternalArticleID, NewsCard

API_KEY = "7346c6661e19434f8fb7fdf9eae6e406"
BASE_URL = "https://api.worldnewsapi.com"

def fetch_news_data(search_query: str | None = None, number: int = 10):
    url = f"{BASE_URL}/search-news"
    params = {
        "api-key": API_KEY,
        "q": search_query,
        "number": number,
        "language": "en",
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        # print(data)  # Add this line to see the full response


        if 'news' in data:
            save_articles(data["news"])  # Save articles from the response
        else:
            print(f"Error fetching data: {data['status']}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def save_articles(articles):
    for article in articles:
        if not ExternalArticleID.objects.filter(external_id=article['id']).exists(): #Check if the ID exists within the external ID table
            news_card = NewsCard(
                title=article.get("title"),
                content=article.get("text"),  
                summary=None,  
                image=article.get("image_url", None), 
                link=article.get("url", ""), 
                is_summarized=False,
            )
            try:
                with transaction.atomic():
                    news_card.save()
                    ExternalArticleID.objects.create(external_id=article['id'], news_card=news_card)
            except Exception as e:
                print(f"Failed to save article {article.get('id')}: {e}")
        else:
            print(f"Article with ID {article['id']} already exists.")



# Example usage
fetch_news_data()
