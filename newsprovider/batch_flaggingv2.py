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
    
    def __init__(self, batch_size=20):
        self.batch_size = batch_size
        self.gptprompts = GPTPrompts()
        self.client = OpenAI()
        self.articles = self.fetch_unflagged_articles()  # Fetch unsummarized articles on initialization

        if not self.articles:
            logger.info("No articles to flag")
            return

    # Return all the unsummarized articles from the database 
    def fetch_unflagged_articles(self):
        return NewsCard.objects.filter(is_flagged=None, id__gt=100)[:self.batch_size]  # Remove id filter in production
    

    def call_flagging_api(self, batch, max_retries: int = 3, wait_time: int = 2):
        retries = 0
        error_message = ''  # Initialize the error_message variable

        while retries < max_retries:
            try:
                # Construct the API prompt with flagger prompt
                prompt_content = self.gptprompts.flagger_prompt + f"Ensure to return {len(batch)} articles" + "\n\n".join(batch)

                logger.debug(f"Complete prompts: {prompt_content}")
                
                # If there was a previous error, include the error message in the prompt
                # if error_message:
                #     prompt_content += f"\n\nPrevious Error: {error_message}"

                # API call
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{'role': 'user', 'content': prompt_content}]
                )

                # Process the API response
                full_response = response.choices[0].message.content
                logger.info(f"Full flagging API response: {full_response}")

                # Split the response (assuming comma-separated values)
                responses = full_response.split(",")

                logger.info(f"Responses object: {responses}")

                # Check if response length matches the batch size
                if len(responses) != len(batch):
                    error_message = f"Response length mismatch: expected {len(batch)}, got {len(responses)}"
                    logger.warning(error_message)
                    raise ValueError(error_message)  # This will trigger the except block

                return responses  # Return responses if correct

            except Exception as e:
                logger.error(f"Error during flagging API call: {e}")
                # error_message = str(e)
                
                retries += 1
    
            # Wait before retrying
            logger.info(f"Retrying {retries}/{max_retries} after {wait_time} seconds...")
            time.sleep(wait_time)  # Delay before retry

        logger.error(f"Max retries ({max_retries}) reached. Returning None for all batch items.")
        return [None] * len(batch)  # Return None for each item in the batch

    def batch_flag_articles(self):
        flagged_statuses = [None] * len(self.articles)

        for i in range(0, len(self.articles), self.batch_size):
            batch = self.articles[i:i + self.batch_size]
            # Create a prompt to ask the AI about potential privacy walls
            prompts = [f"{article.content} <<END>>" for article in batch]

            logger.debug(f"Complete prompts: {prompts}")

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
