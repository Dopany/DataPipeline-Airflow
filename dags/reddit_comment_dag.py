from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable

from datetime import datetime, timedelta
from transformers import pipeline
import pandas as pd
import datetime as dt
import praw

MAX_SEQUENCE_LENGTH = 512
MONTHS = ["December", "November", "October", "September", "August", "July", "June", "May", "April", "March", "February", "January"]
YEARS = ["2024", "2023"]

# api key
"""
    reddit = praw.Reddit(
      client_id="Q0r0aDnOshw7X7M4vHnzIw",
      client_secret="XkMtcZ_96Hw3DPH_aJw_ghbszu7jBg",
      user_agent="testscript by u/purotae",
    )
"""
def get_reddit_comments(**context):
        
    reddit = praw.Reddit(
      client_id=context['params']['client_id'],
      client_secret=context['params']['client_secret'],
      user_agent=context['params']['user_agent'],
    )
    subreddit = reddit.subreddit("wallstreetbets")
    return subreddit


def extract_comment_to_df(**context):
    reddit_comments = pd.DataFrame(columns=['ID', 'BASE_DT', 'COMMENT_CONTENT', 'COMMENT_SENTIMENT'])
    pipe = pipeline("text-classification", model="mwkby/distilbert-base-uncased-sentiment-reddit-crypto")
    subreddit = context['task_instance'].xcom_pull(key = 'return_value', task_ids='get_reddit_comments')
    i = 1
    for year in YEARS:
        for month in MONTHS:
            for day in range(31, 0, -1):
                if year == "2024" and month in ["May", "April", "March"] and day < 10:
                    day = str(day)
                elif day < 10:
                    day = str(day).zfill(2)
                else:
                    day = str(day)
                fixed_title = 'Daily Discussion Thread for {} {}, {}'.format(month, day, year)
                search_results = list(subreddit.search(query=fixed_title, limit=1))

                if search_results:
                    submission = search_results[0]
                else:
                    continue

                if submission.title != fixed_title:
                    continue
                date = dt.date.fromtimestamp(submission.created_utc)
                submission.comments.replace_more(limit=0)
                for comment in submission.comments.list()[:300]:
                    raw_content = comment.body.replace('\n', ' ').replace('\r', ' ').replace('|', ' ').replace(',', '')
                    list_content = strip_text(raw_content, MAX_SEQUENCE_LENGTH)
                    sentiment = judge_setiment(pipe(list_content))
                    reddit_comments.loc[i] = [i, date, raw_content.lower(), sentiment]
                    i += 1
    return reddit_comments

def strip_text(text, max_length=MAX_SEQUENCE_LENGTH):
    results = []
    for i in range(0, len(text), max_length):
        results.append(text[i:i + max_length])
    return results

def judge_setiment(sentiments):
    sum = 0
    for sentiment in sentiments:
        sum += sentiment['score']
    mean = sum / len(sentiment)
    if mean >= 0.5:
        return 'positive'
    elif mean < 0.5:
        return 'negative'

dag = DAG(
    dag_id='reddit_comment_analysis',
    start_date=datetime(2024, 1, 1),
    max_active_runs=1,
    schedule='0 2 * * *',
    catchup=False,
    default_args = {
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
    }
    )

get_reddit_comments = PythonOperator(
    task_id='get_reddit_comments',
    python_callable=get_reddit_comments,
    params = {'client_id': Variable.get('client_id'),
            'client_secret': Variable.get('client_secret'),
            'user_agent': Variable.get('user_agent') },
    dag=dag)

extract_comment_to_df = PythonOperator(
    task_id='extract_comment_to_df',
    python_callable=extract_comment_to_df,
    dag=dag)


get_reddit_comments >> extract_comment_to_df