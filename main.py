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
REDDIT_USER = os.getenv('REDDIT_USER')

reddit_posts = pd.DataFrame(columns = ["Title", "Link", "Type", "Content"])
print(reddit_posts)

reddit = praw.Reddit(
    client_id=REDDIT_ID,
    client_secret=REDDIT_SECRET,
    password=REDDIT_PASSWORD,
    user_agent="Reddit2Notion by u/midnitte",
    username=REDDIT_USER,
)

for item in reddit.user.me().saved(limit=None):
    if isinstance(item, Submission):
        reddit_posts = reddit_posts.append(pd.Series([item.title, item.url, "Post", item.selftext], index=reddit_posts.columns), ignore_index=True)

    else:
        reddit_posts = reddit_posts.append(pd.Series([item.submission.title, "https://reddit.com/" + item.permalink, "Comment", item.body], index=reddit_posts.columns), ignore_index=True)

my_path = "./reddit_posts.csv"
try:
    if os.path.getsize(my_path) > 0:
        # Non empty file exists
        # ... your code ...
        print("File isn't empty")
    else:
        print("File is empty")
        # Empty file exists
        # ... your code ...
except OSError as e:
    print("File doesn't exist")
    # File does not exists or is non accessible
    # ... your code ...

API_KEY = os.getenv('NOTION_TOKEN')
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
    create_page(page['Title'], page['Link'], page['Type'], page['Content'])
