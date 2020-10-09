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
    dz_id_twitter,
    dz_token_twitter,
    team_colors,
)
from discord import Webhook, RequestsWebhookAdapter
from discord.ext import commands, tasks
# import re
import praw
from pymongo import MongoClient
from cog.webhook import reddit_webhook


# Setup connection to mongodb collection
reddit_db = MongoClient(mongserver).twitter_db.reddit

# Filter for our aggregation
pipelineP = [{"$match": {"posted": False}}]

webhook = Webhook.partial(
    webhook_id_reddit, webhook_token_reddit, adapter=RequestsWebhookAdapter()
)
# webhook = Webhook.partial(
#     dz_id_twitter, dz_token_twitter, adapter=RequestsWebhookAdapter()
# )

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
        filterPosts(reddit_db, reddit, pipelineP, webhook, name_list)

    @bgtask.before_loop
    async def before_task(self):
        print("waiting...")
        await self.client.wait_until_ready()


def find_color(title, handles):
    title = title.lower()
    for handle in handles:
        for name in handles[handle]:
            if title.find(name) >= 0:
                return handle.lower()
    return "f1"


# Grab post from a subreddit and only return a url if it hasn't been returned before
def ping_reddit(sub, count, database, handles):
    subred = reddit.subreddit(sub)
    for post in subred.hot(limit=10):
        if post.ups > count and not post.stickied:
            # Check in database to see if we've posted this submission before
            if database.find_one({"post_id": post.id}):
                pass
            else:
                color = find_color(post.title, handles)
                data = {
                    "post_id": post.id,
                    "title": post.title,
                    "url": post.url,
                    "color": team_colors[color],
                    "posted": False,
                }
                database.insert_one(data).inserted_id
                # Haven't posted before so store submission ID in database


def filterPosts(database, reddit, pipeline, webhook, handles):
    """
    Look through our aggregate(contains filtered posts) for any
    documents, format them for discord, and then send them in a
    discord webhook
    """

    lst = []
    empty = 0  # remains 0 if there are no entries for the aggregation

    for sub in sublist:
        ping_reddit(sub[0], sub[1], database, handles)
    for doc in database.aggregate(pipeline):
        empty += 1
        # Extract the information from the db.
        lst.append([doc["title"], doc["url"], doc["color"]])
        # Update the db to show that we've posted this entry
        database.update_one({"_id": doc["_id"]}, {"$set": {"posted": True}})

    if empty > 0:
        # Format for embed
        data = reddit_webhook(lst)
        # Send message
        print('Found a post(s) and sending it to discord')
        webhook.send(embeds=data)
    

def setup(client):
    client.add_cog(Reddit(client))
