import logging
import os
import re
import time
from django.db import transaction
from openai import OpenAI

from newsprovider.models import NewsCard
from .ai_prompt import GPTPrompts

import logging

# # Get the current file's base name (without directory and extension)
# current_filename = os.path.splitext(os.path.basename(__file__))[0]

# # Set up logging configuration with a file handler specific to this file
# log_file = f"{current_filename}.log"

# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s [%(levelname)s] %(message)s',
#     handlers=[
#         logging.FileHandler(log_file),  # Log to a file specific to this script
#         logging.StreamHandler()  # Optionally log to the console
#     ]
# )

# Set up the logger
logger = logging.getLogger('qwiknews')

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qwiknews.settings')

# # Initialize Django
# django.setup()

# gptprompts = GPTPrompts()

# client = OpenAI()

# BATCH_SIZE = 10 #Ensure that this batch size remains consistent for all the batch requests (flagging and summarization)

class SummarizationProcess:
    def __init__(self, batch_size: int = 10) -> None:
        self.batch_size = batch_size
        self.gptprompts = GPTPrompts()
        self.client = OpenAI()
        self.articles = self.fetch_unsummarized_articles()

        if not self.articles:
            logger.info("No articles to summarize")

    def fetch_unsummarized_articles(self):
        return NewsCard.objects.filter(is_summarized=False, id__gt=100)  # remove id filter for production

    def batch_summarize_articles(self):
        # Initialize the all_summaries list 
        all_summaries = [None] * len(self.articles)

        for i in range(0, len(self.articles), self.batch_size):
            # Slice the articles list by the batch size
            batch = self.articles[i:i + self.batch_size]
            
            # Add an index to each article in the batch and create the prompts to be fed to OpenAI
            prompts = [f"Article {idx}: {article.content}" for idx, article in enumerate(batch, start=1)]
            
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            'role': 'system',
                            'content': f"{self.gptprompts.summarize_prompt}"
                        },
                        {'role': 'user', 'content': "\n\n".join(prompts)}
                    ]
                )
                
                full_response = response.choices[0].message.content
                time.sleep(20)  # API rate limit workaround
                
                # Split the response into individual summaries
                summaries = full_response.split("Summary for Article")[1:]  # Remove the first empty split
                
                # Add summaries by their index to the initial list
                for idx, summary in enumerate(summaries):
                    article_idx = i + idx
                    if article_idx < len(all_summaries):
                        all_summaries[article_idx] = summary.strip()
                        logger.debug(f"Processed summary for article at index {article_idx}: {all_summaries[article_idx][:50]}...")
                
                logger.info(f"Batch of {len(batch)} articles summarized successfully")
            except Exception as e:
                logger.error(f"Error summarizing batch starting at index {i}: {str(e)}")
        
        time.sleep(5)
        return all_summaries

    def process_summarized_articles(self):

        if not self.articles:
            logger.info('No articles to process for summarization')

        summaries = self.batch_summarize_articles()

        logger.info(f"Number of articles: {len(self.articles)}, Number of summaries: {len(summaries)}")

        # Add an index to the summaries list
        for idx, summary in enumerate(summaries):
            logger.debug(f"Summary at index {idx}: {summary[:50] if summary else 'None'}...")

        with transaction.atomic():
            # pair each article to a summary
            for article, summary in zip(self.articles, summaries):
                if summary:
                    cleaned_summary = self.clean_summary(summary)
                    article.summary = cleaned_summary
                    article.is_summarized = True
                    article.is_flagged = None
                    article.save()
                    logger.info(f"Article {article.id} updated with summary")
                else:
                    logger.warning(f"Failed to summarize article {article.id}: Empty or None summary")

    @staticmethod
    def clean_summary(summary):
        return re.sub(r'^\d+:\s*', '', summary.strip())
