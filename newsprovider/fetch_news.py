from datetime import datetime, timedelta
import django
import re
import os
import pickle
import requests
from django.utils import timezone
from django.db import transaction



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qwiknews.settings')
django.setup()

from newsprovider.models import Category, ExternalArticleID, NewsCard

API_KEY = "7346c6661e19434f8fb7fdf9eae6e406"
BASE_URL = "https://api.worldnewsapi.com"

PICKLE_FILE = 'offset_data.pkl'

def load_offset() -> int:
    """Load the offset value from the pickle file. If the file doesn't exist, return 0."""
    if os.path.exists(PICKLE_FILE):
        with open(PICKLE_FILE, 'rb') as file:
            return pickle.load(file)
    return 0  # Default offset if no file exists

def save_offset(offset: int) -> None:
    """Save the offset value to the pickle file."""
    with open(PICKLE_FILE, 'wb') as file:
        pickle.dump(offset, file)


def fetch_news_data(search_query: str = None, number: int = 30, offset: int = None):
    
    if offset is None:
        offset = load_offset()

    print(f'Current offset value in fetch_news_data is :{offset}')

    url = f"{BASE_URL}/search-news"
    params = {
        "api-key": API_KEY,
        "q": search_query,
        "number": number,
        "offset": offset,
        "language": "en",
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        if 'news' in data:
            offset = save_articles(data["news"], offset)  # Save articles from the response
            save_offset(offset) #save the new offset value to pickle
        else:
            print(f"Error fetching data: {data['status']}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")



def remove_emojis(text):
    """Remove emojis and special characters from the given text."""
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)



def save_articles(articles, offset: int):



    for article in articles:
        if not ExternalArticleID.objects.filter(external_id=article['id']).exists():  # Check if the ID exists within the external ID table
            
            # Sanitize title and content
            title = article.get("title", "")
            sanitized_title = remove_emojis(title)

            content = article.get("text", "")
            sanitized_content = remove_emojis(content)

            category_name = article.get("category", None)  # Get the category name from the article

            news_card = NewsCard(
                title=sanitized_title,
                content=sanitized_content,
                summary=None,
                image=article.get("image", None),
                link=article.get("url", ""),
                is_summarized=False,
                categories=article.get("category", None)
            )
            try:
                with transaction.atomic():
                    news_card.save()
                    ExternalArticleID.objects.create(external_id=article['id'], news_card=news_card)

                    # Handle category association
                    if category_name:
                        # Normalize category_name to lowercase to ensure case-insensitive matching
                        category_name_lower = category_name.lower()
                        
                        # Try to find the category with a case-insensitive match
                        category, created = Category.objects.get_or_create(
                            name__iexact=category_name_lower,  # Case-insensitive query
                            defaults={'name': category_name_lower}  # If not found, create with the lowercase
                        )
                        # Add the category to the ManyToManyField
                        news_card.categories.add(category)

            except Exception as e:
                print(f"Failed to save article {article.get('id')}: {e}")
                continue
                
        else:
            print(f"Article with ID {article['id']} already exists.")
            
        offset += 1
        
    # Get current time
    now = datetime.now()
    previous_minute = now - timedelta(minutes=1)

    # Reset offset if the current hour is different from the previous minute's hour
    if now.hour != previous_minute.hour:
        offset = 0  # Reset offset
        print("Offset reset to 0.")


    return offset



# Example usage
# fetch_news_data()
