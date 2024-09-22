import time
from celery import shared_task
from .fetch_news import fetch_news_data
from .summarization_task import process_summarized_articles, fetch_unsummarized_articles

def fetch_summarize_and_save():

    fetch_news_data() #Calls save_articles with saves the data in the db

    time.sleep(2)

    articles = fetch_unsummarized_articles() #Returns the articles in the db that have not been summarized
    
    process_summarized_articles(articles=articles) #Calls summarize_article (GPT-wrapper), and saves summary in the db