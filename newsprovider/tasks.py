import logging
from celery import shared_task
from .fetch_news import fetch_news_data
from .batch_summarizationv3 import SummarizationProcess
from .batch_flaggingv2 import FlaggingProcess
from .models import NewsCard
from django.db.models import Count
from django.db import transaction

# Get the logger for this module
logger = logging.getLogger('qwiknews')

@shared_task
def fetch_news():
    logger.info('Running fetch_news task')

    try:
        fetch_news_data()  # Calls save_articles which saves the data in the db
    except Exception as e:
        logger.error(f"Error in running fetch_news task: {e}")

# @shared_task(bind=True)
@shared_task
def summarize_articles():
    logger.info('Running summarize_articles task')

    try:
        summarization_process = SummarizationProcess()
        summarization_process.process_summarized_articles()  # Processes articles for summarization
    except Exception as e:
        logger.error(f"Error in running summarize_articles task: {e}")
    # finally:
    #     self.apply_async(countdown=1)

@shared_task
def flag_articles(batch_size=10):
    logger.info('Running flag_articles task')

    try:
        flagging_process = FlaggingProcess(batch_size=batch_size)
        flagging_process.process_flagged_articles()  # Processes articles for flagging
    except Exception as e:
        logger.error(f"Error in running flag_articles task: {e}")

@shared_task
def remove_duplicate_news_cards():
    logger.info('Running remove_duplicate_news_cards task')

    try:
        with transaction.atomic():
            # Find duplicate titles
            duplicates = NewsCard.objects.values('title').annotate(
                title_count=Count('title')
            ).filter(title_count__gt=1)

            for duplicate in duplicates:
                title = duplicate['title']
                # Get all news cards with this title, ordered by id (assuming newer entries have higher ids)
                cards = NewsCard.objects.filter(title=title).order_by('id')
                
                # Keep the latest entry (last in the list) and delete the rest
                to_delete = cards[:-1]
                deleted_count = to_delete.delete()[0]
                
                logger.info(f"Deleted {deleted_count} duplicate entries for title: {title}")

        logger.info('Finished removing duplicate news cards')
    except Exception as e:
        logger.error(f"Error in running remove_duplicate_news_cards task: {e}")

# Add this task to your CELERY_BEAT_SCHEDULE in settings.py to run it periodically
