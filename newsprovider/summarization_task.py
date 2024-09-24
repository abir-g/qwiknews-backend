import os
import django
from openai import OpenAI
from django.conf import settings
from django.db import transaction

# Set the environment variable for Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qwiknews.settings')

# Initialize Django
django.setup()

from newsprovider.models import NewsCard 
from newsprovider.ai_prompt import prompt  


# Initialize OpenAI client
client = OpenAI()

def fetch_unsummarized_articles():
    return NewsCard.objects.filter(is_summarized=False, id__gt=100)

def summarize_article(article):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Fixed model name
            messages=[
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': article.content},
            ]
        )
        print(f'Article {article.id} summarized SUCCESSFULLY')
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error summarizing article {article.id}: {e}")
        return None

def process_summarized_articles(articles):
    # articles = fetch_unsummarized_articles()
    
    for article in articles:
        summary = summarize_article(article)

        if summary:
            try:
                with transaction.atomic():
                    article.summary = summary
                    article.is_summarized = True
                    article.save()
            except Exception as e:
                print(f"Transaction failed for article {article.id}: {e}")

# process_summarized_articles()