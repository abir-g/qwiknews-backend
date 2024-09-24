import logging
import os
import re
import time
import django
from django.db import transaction
from openai import OpenAI

import logging

# Get the current file's base name (without directory and extension)
current_filename = os.path.splitext(os.path.basename(__file__))[0]

# Set up logging configuration with a file handler specific to this file
log_file = f"{current_filename}.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),  # Log to a file specific to this script
        logging.StreamHandler()  # Optionally log to the console
    ]
)

# Set up the logger
logger = logging.getLogger(current_filename)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qwiknews.settings')

# Initialize Django
django.setup()

from newsprovider.models import NewsCard
from .ai_prompt import prompt

client = OpenAI()

# return all the unsummarized articles from the database 
def fetch_unsummarized_articles():
    return NewsCard.objects.filter(is_summarized=False, id__gt=100)


# Remove the number prefix and any leading/trailing whitespace
def clean_summary(summary):
    cleaned = re.sub(r'^\d+:\s*', '', summary.strip())
    return cleaned


def batch_summarize_articles(articles, batch_size=10):
    # Initialize the all_summaries list 
    all_summaries = [None] * len(articles)
    
    for i in range(0, len(articles), batch_size):
        # Slice the articles list till the batch size
        batch = articles[i:i+batch_size]
        
        # Add an index to each article in the batch using enumerate and create the prompts to be fed to OpenAI
        prompts = [f"Article {idx}: {article.content}" for idx, article in enumerate(batch, start=1)]
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {'role': 'system', 'content': f"{prompt}. Provide a summary for each article, prefixed with 'Summary for Article X:', where X is the article number."},
                    {'role': 'user', 'content': "\n\n".join(prompts)}
                ]
            )
            
            full_response = response.choices[0].message.content
            print(f"Full API response: {full_response}")
            
            # Split the response into individual summaries
            summaries = full_response.split("Summary for Article")[1:]  # Remove the first empty split
            
            # Add an index to the summaries generated
            for idx, summary in enumerate(summaries):
                # Add the current batch starting number (i)
                article_idx = i + idx

                if article_idx < len(all_summaries):
                    # Add the summaries by their index to the initial list
                    all_summaries[article_idx] = summary.strip()
                    logger.debug(f"Processed summary for article at index {article_idx}: {all_summaries[article_idx][:50]}...")
            
            logger.info(f"Batch of {len(batch)} articles summarized successfully")
        except Exception as e:
            logger.error(f"Error summarizing batch starting at index {i}: {str(e)}")
    
    time.sleep(5)
    
    return all_summaries


def process_summarized_articles(articles):
    summaries = batch_summarize_articles(articles)
    
    logger.debug(f"Number of articles: {len(articles)}, Number of summaries: {len(summaries)}")

    # Add an index to the the all_summaries list
    for idx, summary in enumerate(summaries):
        logger.debug(f"Summary at index {idx}: {summary[:50] if summary else 'None'}...")
    
    with transaction.atomic():
        # pair each article to a summary
        for article, summary in zip(articles, summaries):
            if summary:
                cleaned_summary = clean_summary(summary=summary)
                article.summary = cleaned_summary
                article.is_summarized = True
                article.save()
                logger.info(f"Article {article.id} updated with summary")
            else:
                logger.warning(f"Failed to summarize article {article.id}: Empty or None summary")

# Usage
# articles = fetch_unsummarized_articles()
# process_summarized_articles(articles)