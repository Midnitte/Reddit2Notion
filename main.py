import os
import praw
from praw.models import Comment, Submission
from dotenv.main import find_dotenv
from notion_client import Client
from notion_client.api_endpoints import DatabasesEndpoint, PagesEndpoint
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

REDDIT_ID = os.getenv('REDDIT_ID')
REDDIT_SECRET = os.getenv('REDDIT_SECRET')
REDDIT_PASSWORD = os.getenv('REDDIT_PASSWORD')

reddit_posts = pd.DataFrame(columns = ["Title", "Link", "Type", "Content"])
print(reddit_posts)

reddit = praw.Reddit(
    client_id=REDDIT_ID,
    client_secret=REDDIT_SECRET,
    password=REDDIT_PASSWORD,
    user_agent="testscript by u/midnitte",
    username="midnitte",
)

for item in reddit.user.me().saved(limit=None):
    if isinstance(item, Submission):
        reddit_posts = reddit_posts.append(pd.Series([item.title, item.url, "Post", item.selftext], index=reddit_posts.columns), ignore_index=True)

    else:
        reddit_posts = reddit_posts.append(pd.Series([item.submission.title, "https://reddit.com/" + item.permalink, "Comment", item.body], index=reddit_posts.columns), ignore_index=True)


API_KEY = os.getenv('NOTION_TOKEN')

print(API_KEY)
notion = Client(auth=API_KEY)

DB_NAME = "Test Reddit"

def search_db(dbname):
    db = notion.search(**{
        'query': dbname,
        'property': 'object',
        'value': 'database'
    })
    return db['results'][0]['id']

my_database = notion.databases.retrieve(database_id=search_db(DB_NAME))

def create_page(page_title, link_url, post_type, body_content):
    print(f"Creating [{page_title}]")
    notion.pages.create(
        parent={'database_id': my_database['id']},
        properties={
    'Name': {'title': [{'text': {'content': page_title}}]},
    'Link': {'type': 'url', 'url': link_url},
    'Type': {'rich_text': [{'text': {'content': post_type}}]}
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
                    'content': body_content,
                },
                },
            ],
            },
        },
        ],
    )
#create_page("Test Title", "https://test.com/func", "Comment", "ibsa dera dee")

for index, page in reddit_posts.iterrows():
    create_page(page['Title'], page['Link'], page['Type'], page['Content'])
