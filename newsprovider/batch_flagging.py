import logging
import os
import re
import time
import django
from django.db import transaction
from openai import OpenAI

import logging

from newsprovider.models import NewsCard
from .ai_prompt import GPTPrompts
# # Get the current file's base name (without directory and extension)
# current_filename = os.path.splitext(os.path.basename(__file__))[0]

# # Set up logging configuration with a file handler specific to this file
# log_file = f"{current_filename}.log"

# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s [%(levelname)s] %(message)s',
#     handlers=[
#         logging.FileHandler(log_file, mode='a'),  # Log to a file specific to this script
#         logging.StreamHandler()  # Optionally log to the console
#     ]
# )

# Set up the logger
logger = logging.getLogger('qwiknews')

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qwiknews.settings')

# # Initialize Django
# django.setup()


# BATCH_SIZE = 10 #Ensure that this batch size remains consistent for all the batch requests (flagging and summarization)


class FlaggingProcess:
    
    def __init__(self, batch_size):
        self.batch_size = batch_size
        self.gptprompts = GPTPrompts()
        self.client = OpenAI()
        self.articles = self.fetch_unflagged_articles()  # Fetch unsummarized articles on initialization

        if not self.articles:
            logger.info("No articles to flag")
            return

    # Return all the unsummarized articles from the database 
    def fetch_unflagged_articles(self):
        return NewsCard.objects.filter(is_flagged=None, id__gt=100)  # Remove id filter in production

    def call_flagging_api(self, batch, max_retries:int = 3, wait_time: int = 2):
        retries = 0
        error_message = ''  # Initialize the error_message variable
        while retries < max_retries:
            try:
                messages=[{'role': 'user', 'content': self.gptprompts.flagger_prompt + "\n\n".join(batch)}]

                # If it's a retry, add the error message to the prompt
                if retries > 0:
                    messages[0]['content'] += f"\n\nPrevious Error: {error_message}"

                # Call the API
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                )

                # Process the response to get flagged statuses
                full_response = response.choices[0].message.content
                logging.info(f"Full MARKER API response: {full_response}")

                responses = full_response.split(",")  # GPT has been instructed to supply comma-separated format

                # Check if response length matches batch size
                if len(responses) == len(batch):
                    return responses  # If correct, return responses
                else:
                    error_message = f"Response length mismatch: expected {len(batch)}, got {len(responses)}"
                    
            except Exception as e:
                logging.info(f"API call failed: {e}")
                error_message = str(e)

                # Retry logic
                retries += 1
                logging.info(f"Retrying {retries}/{max_retries}...")
                time.sleep(wait_time)

        logger.warning(f"Failed to get a valid response after {max_retries} attempts, returning None for all items in batch")
        return [None] * len(batch)

    def batch_flag_articles(self):
        flagged_statuses = [None] * len(self.articles)

        for i in range(0, len(self.articles), self.batch_size):
            batch = self.articles[i:i + self.batch_size]
            # Create a prompt to ask the AI about potential privacy walls
            prompts = [f"{article.content} <<END>>" for article in batch]

            try:
                responses = self.call_flagging_api(prompts, wait_time=20)

                for idx, response in enumerate(responses):
                    article_idx = i + idx
                    if article_idx < len(flagged_statuses):
                        flagged_statuses[article_idx] =  None if response is None else "yes" in response.lower()  # Set True/False based on response, or None if response fails

                logger.info(f"Batch of {len(batch)} articles flagged successfully")
                time.sleep(20) #work around to api rate limits

            except Exception as e:
                logger.error(f"Error flagging batch starting at index {i}: {str(e)}")

        return flagged_statuses

    def process_flagged_articles(self):
        
        if not self.articles:
            logger.info("No articles to process for flagging.")
            return  # Exit if no articles to process
        
        flagged_statuses = self.batch_flag_articles()

        with transaction.atomic():
            # pair each article to a summary
            for article, is_flagged in zip(self.articles, flagged_statuses):
                article.is_flagged = is_flagged
                article.save()
                logger.info(f"Article {article.id} updated with flagged status")
