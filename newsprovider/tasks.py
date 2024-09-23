import time
from celery import shared_task
from .fetch_news import fetch_news_data
from .summarization_task import process_summarized_articles, fetch_unsummarized_articles


@shared_task
def fetch_summarize_and_save():
    print('Running MAIN task')

    try:
            
        fetch_news_data() #Calls save_articles with saves the data in the db

        time.sleep(2)

        articles = fetch_unsummarized_articles() #Returns the articles in the db that have not been summarized
        
        process_summarized_articles(articles=articles) #Calls summarize_article (GPT-wrapper), and saves summary in the db
        
    except Exception as e:
        print(f"Error in running main task: {e}")