from functools import wraps
import logging
import re
import time
from django.db import transaction
from openai import OpenAI

from newsprovider.models import NewsCard
from .ai_prompt import GPTPrompts

import logging

logger = logging.getLogger('qwiknews')

class SummarizationProcess:
    def __init__(self, batch_size: int = 10) -> None:
        self.batch_size = batch_size
        self.gptprompts = GPTPrompts()
        self.client = OpenAI()
        self.articles = self.fetch_unsummarized_articles()

        if not self.articles:
            logger.info("No articles to summarize")

    def fetch_unsummarized_articles(self):
        return NewsCard.objects.filter(is_summarized=False, id__gt=100)[:self.batch_size]  # remove id filter for production
    

    def retry(retries=3, delay=5):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                for attempt in range(retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                        if attempt == retries - 1:
                            raise
                        time.sleep(delay)
            return wrapper
        return decorator


    @retry(retries=3, delay=2)
    def call_openai_api(self, prompts, system_content):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {'role': 'system', 'content': system_content},
                {'role': 'user', 'content': "\n\n".join(prompts)}
            ]
        )
        return response.choices[0].message.content


    def process_summaries(self, full_response, batch_size):
        summaries = full_response.split("Summary for Article")[1:]
        if len(summaries) != batch_size:
            error_message = (f"Expected {batch_size} summaries, got {len(summaries)}")
            return None, error_message
        return [summary.strip() for summary in summaries], None


    @retry(retries=3, delay=5)
    def summarize_batch(self, prompts, error_message):
        # Construct the system content and include error_message if present
        system_content = f"{self.gptprompts.summarize_prompt}. Provide a summary for each article, prefixed with 'Summary for Article X:', where X is the article number."
        if error_message:
            system_content += f" {error_message}"

        full_response = self.call_openai_api(prompts, system_content)
        logger.info(f"API Response: {full_response[:100]}...")
        
        summaries, error_message = self.process_summaries(full_response, len(prompts))
        
        if error_message:
            logger.warning(f"Error in processing summaries: {error_message}")
            raise ValueError(error_message)  # Raise an exception to trigger retry
            
        return summaries
    

    def batch_summarize_articles(self):
        all_summaries = [None] * len(self.articles)

        for i in range(0, len(self.articles), self.batch_size):
            batch = self.articles[i:i + self.batch_size]
            prompts = [f"Article {idx}: {article.content}" for idx, article in enumerate(batch, start=1)]
            
            error_message = ""  # Initialize error message

            # Call the new method with retry logic
            summaries = self.summarize_batch(prompts, error_message)

            for idx, summary in enumerate(summaries):
                article_idx = i + idx
                if article_idx < len(all_summaries):
                    all_summaries[article_idx] = summary
                    logger.info(f"Processed summary for article {article_idx}: {summary[:50]}...")

            logger.info(f"Batch of {len(batch)} articles summarized successfully")
            time.sleep(20)  # API rate limit workaround

        return all_summaries
    

    def process_summarized_articles(self):

        if not self.articles:
            logger.info('No articles to process for summarization')
            return

        summaries = self.batch_summarize_articles()

        logger.info(f"Number of articles: {len(self.articles)}, Number of summaries: {len(summaries)}")

        # Add an index to the summaries list
        for idx, summary in enumerate(summaries):
            logger.info(f"Summary at index {idx}: {summary[:50] if summary else 'None'}...")

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
