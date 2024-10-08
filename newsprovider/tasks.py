import logging
from celery import shared_task
from .fetch_news import fetch_news_data
from .batch_summarizationv2 import SummarizationProcess
from .batch_flagging import FlaggingProcess

# Get the logger for this module
logger = logging.getLogger(__name__)

@shared_task
def fetch_news():
    logger.info('Running fetch_news task')

    try:
        fetch_news_data()  # Calls save_articles which saves the data in the db
    except Exception as e:
        logger.error(f"Error in running fetch_news task: {e}")

@shared_task
def summarize_articles(batch_size=10):
    logger.info('Running summarize_articles task')

    try:
        summarization_process = SummarizationProcess(batch_size=batch_size)
        summarization_process.process_summarized_articles()  # Processes articles for summarization
    except Exception as e:
        logger.error(f"Error in running summarize_articles task: {e}")

@shared_task
def flag_articles(batch_size=10):
    logger.info('Running flag_articles task')

    try:
        flagging_process = FlaggingProcess(batch_size=batch_size)
        flagging_process.process_flagged_articles()  # Processes articles for flagging
    except Exception as e:
        logger.error(f"Error in running flag_articles task: {e}")
