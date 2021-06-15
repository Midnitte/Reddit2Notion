# Reddit2Notion
A script that converts saved reddit content into Notion pages within a database.

![Header Logo](logo.png)


# How to get started
First you will need to register a [Reddit Application](https://www.reddit.com/prefs/apps/) and make a new [Notion Integration](https://developers.notion.com/),. Copy your Notion token, Reddit ID, Secret, password, and username into a `.env` file.
```
NOTION_TOKEN=""
REDDIT_ID=""
REDDIT_SECRET=""
REDDIT_PASSWORD=""
REDDIT_USER=""
```

In Notion, create a new database called `Test Reddit` (or import [this template](https://www.notion.so/midnitte/c099bc8bb94e46dd80e839f949b52bd1?v=e30c1ee61617401a9fcd180a073958b9)). You can then run the script.
