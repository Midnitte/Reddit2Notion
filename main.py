#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A python script to convert saved Reddit content from your account into pages within a Notion database."""
__author__ = ["Christopher Norulak"]
__version__ = "0.0.1"

import os
import sys
import logging
import praw
from datetime import datetime
import pytz
from praw.models import Comment, Submission
from notion_client import Client
from notion_client.api_endpoints import DatabasesEndpoint, PagesEndpoint
from dotenv import load_dotenv
import pandas as pd

logging.basicConfig(level=logging.INFO)
load_dotenv()

REDDIT_ID = os.getenv('REDDIT_ID')
REDDIT_SECRET = os.getenv('REDDIT_SECRET')
REDDIT_PASSWORD = os.getenv('REDDIT_PASSWORD')
REDDIT_USER = os.getenv('REDDIT_USER')

DB_NAME = os.getenv('NOTION_DB')
API_KEY = os.getenv('NOTION_TOKEN')
notion = Client(auth=API_KEY)
# Set our working directory to the current directory where the file is located.
os.chdir(os.path.dirname(sys.argv[0]))
# Set timezone to local zone so we can convert time to local time.
tz = datetime.now().astimezone().tzinfo

reddit = praw.Reddit(
    client_id=REDDIT_ID,
    client_secret=REDDIT_SECRET,
    password=REDDIT_PASSWORD,
    user_agent="Reddit2Notion by u/midnitte",
    username=REDDIT_USER,
)

reddit_posts = pd.DataFrame(columns = ["Title", "Link", "Type", "Subreddit", "Created", "Content"])

for item in reddit.user.me().saved(limit=None):
    if isinstance(item, Submission):
        reddit_posts = reddit_posts.append(pd.Series([item.title, item.url, "Post", item.subreddit.display_name, item.created_utc, item.selftext], index=reddit_posts.columns), ignore_index=True)
        logging.info(f'Adding post: {item.title}')
    else:
        reddit_posts = reddit_posts.append(pd.Series([item.submission.title, "https://reddit.com/" + item.permalink, "Comment", item.submission.subreddit.display_name, item.created_utc, item.body], index=reddit_posts.columns), ignore_index=True)
        logging.info(f'Adding comment: {item.submission.title}')

def convert_time(value):
    return datetime.fromtimestamp(value, tz).isoformat()
# Convert PRAW's time to Notion's usage of ISO 8601
reddit_posts['Created'] = reddit_posts['Created'].apply(lambda x :convert_time(x))

try:
    if os.path.getsize('./reddit_posts.csv') > 0:
        # TODO: Compare reddit_posts to saved file and only create the unique content.
        logging.info("File isn't empty")
        compare_db = pd.read_csv(r'./reddit_posts.csv') 
        logging.info(f"loaded file: ")
    else:
        logging.info("File is empty")
        reddit_posts.to_csv(r'./reddit_posts.csv', mode='a')
except OSError as e:
    logging.info("File doesn't exist")
    reddit_posts.to_csv(r'./reddit_posts.csv')


def search_db(dbname):
    db = notion.search(**{
        'query': dbname,
        'property': 'object',
        'value': 'database'
    })
    logging.info(f"Found database {db['results'][0]['id']}")
    return db['results'][0]['id']

my_database = notion.databases.retrieve(database_id=search_db(DB_NAME))

def create_page(page_title, link_url, post_type, subreddit, created, body_content):
    logging.info(f"Creating [{page_title}]")
    notion.pages.create(
        parent={'database_id': my_database['id']},
        properties={
    'Name': {'title': [{'text': {'content': page_title}}]},
    'Link': {'type': 'url', 'url': link_url},
    'Type': {'rich_text': [{'text': {'content': post_type}}]},
    # Note: I would like to use selector here, but Notion doesn't seem to let you create selector options via the API
    'Subreddit': {'rich_text': [{'text': {'content': subreddit}}]},
    'Date': {"date": {"start": created}},
},
        children= [
        {
            'object': 'block',
            'type': 'paragraph',
            'paragraph': {
            'text': [
                {
                'type': 'text',
                'text': {
                    # Get the first 1000 characters to prevent triggering Notion API limit
                    'content': body_content[0:1000],
                },
                },
            ],
            },
        },
        ],
    )

for index, page in reddit_posts.iterrows():
    create_page(page['Title'], page['Link'], page['Type'], page['Subreddit'], page['Created'], page['Content'])
