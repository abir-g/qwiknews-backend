from openai import OpenAI
from .models import NewsCard
from .ai_prompt import prompt
from django.conf import settings
from django.db import transaction

client = OpenAI()

def fetch_unsummarized_articles():
    return NewsCard.objects.filter(is_summarized=False)

def summarize_article(article):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Fixed model name
            messages=[
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': article.content},
            ]
        )
        return completion['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error summarizing article {article.id}: {e}")
        return None

def process_summarized_articles():
    articles = fetch_unsummarized_articles()
    
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
