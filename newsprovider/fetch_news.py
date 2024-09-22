import os
import requests
from django.utils import timezone
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qwiknews.settings')
django.setup()

from newsprovider.models import NewsCard

API_KEY = "7346c6661e19434f8fb7fdf9eae6e406"
BASE_URL = "https://api.worldnewsapi.com"

def fetch_news_data(search_query: str | None = None, number: int = 5):
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
        try:
            news_card = NewsCard.objects.create(
                title=article.get("title"),
                content=article.get("text"),  
                summary=None,  
                image=article.get("image_url", None), 
                link=article.get("url", ""), 
                is_summarized=False,
            )

        except Exception as e:
            print(f"Failed to save article {article.get('id')}: {e}")


# Example usage
fetch_news_data()
