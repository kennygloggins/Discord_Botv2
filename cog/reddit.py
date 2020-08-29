# By: Kenny_G_Loggins
# Created on: 8/2/20, 3:57 PM
# File: reddit_bot_tut.py
# Project: Reddit_bot

from config import (
    mongserver,
    name_list,
    reddit_frequency,
    sublist,
    webhook_id_reddit,
    webhook_token_reddit,
)
from discord import Webhook, RequestsWebhookAdapter
from discord.ext import commands, tasks
import re
import praw
from pymongo import MongoClient
from cog.webhook import reddit_webhook


# Setup connection to mongodb collection
server = MongoClient(mongserver)
db = server.twitter_db
posts = db.reddit_test

webhook = Webhook.partial(
    webhook_id_reddit, webhook_token_reddit, adapter=RequestsWebhookAdapter()
)

# Grab bot info from praw.ini
reddit = praw.Reddit("bot1")


class Reddit(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.bgtask.start()

    def cog_unload(self):
        self.bgtask.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Reddit extension loaded.")

    @tasks.loop(minutes=reddit_frequency)
    async def bgtask(self):
        printParsedReddit()

    @bgtask.before_loop
    async def before_task(self):
        print("waiting...")
        await self.client.wait_until_ready()


def find_name(fname):
    for key, value in name_list.items():
        for x in value:
            if re.search(x, fname):
                return key
    return "F1"


# Grab post from a subreddit and only return a url if it hasn't been returned before
def ping_reddit(sub, count):
    danger = reddit.subreddit(sub)
    new_title = []
    new_post = []
    new_name = []
    for post in danger.hot(limit=10):
        if post.ups > count and not post.stickied:
            # Check in database to see if we've posted this submission before
            if db.reddit_test.find_one({"post_id": post.id}):
                pass
            else:
                post_id = {"post_id": post.id}
                postdb_id = posts.insert_one(post_id).inserted_id
                # Haven't posted before so store submission ID in database and
                # append the title and url onto our lists
                new_title.append(post.title)
                new_post.append(post.url)
    for name in new_title:
        new_name.append(find_name(name.lower()))
    return new_title, new_post, new_name


def printParsedReddit():
    for item in sublist:
        titles, posts, names = ping_reddit(item[0], item[1])
        for title, post, name in zip(titles, posts, names):
            data = reddit_webhook(title, post, name)
            webhook.send(embed=data)


def setup(client):
    client.add_cog(Reddit(client))
