from bs4 import BeautifulSoup
from cog.webhook import twitter_webhook
from config import (
    mongserver,
    twitter_words,
    twitter_handles,
    team_colors,
    dz_id_twitter,
    dz_token_twitter,
    bl_id_twitter,
    bl_token_twitter,
)
from discord import Webhook, RequestsWebhookAdapter
from discord.ext import commands, tasks
import requests
from pymongo import MongoClient


# Setup connection to mongodb collection
server = MongoClient(mongserver)
db = server.twitter_db
posts = db.tweets
# Filter for our aggregation
pipeline = [{"$match": {"text": {"$regex": twitter_words}, "posted": False}}]

# Variable for server to post in
SET_SERVER = "dz"


class Twitter(commands.Cog):
    """
    This defines our twitter cog for discord. Commands for server
    change and our loop for parsing twitter are here.
    """

    def __init__(self, client):
        self.client = client
        self.bgtask.start()

    # Break loop when we unload the cog
    def cog_unload(self):
        self.bgtask.cancel()

    # Prints to console when ready
    @commands.Cog.listener()
    async def on_ready(self):
        print("Twitter extension loaded.")

    # Commands for discord to chose server to post to
    @commands.command()
    async def servDZ(self, ctx):
        await ctx.send("```Selecting server Danger Zone.```")
        SET_SERVER = "dz"

    @commands.command()
    async def servBL(self, ctx):
        await ctx.send("```Selecting server Boot Lickers.```")
        SET_SERVER = "bl"

    # loop for parsing twitter
    @tasks.loop(minutes=5)  # twitter_frequency
    async def bgtask(self):
        printParsedTweet()

    @bgtask.before_loop
    async def before_task(self):
        print("waiting...")
        await self.client.wait_until_ready()


class TweetParser:
    """
    Take a tweet's information and rebundle it for use in a webhook.
    The plan is to recreate a conversation when there is one and also
    search for keywords.
    """

    def __init__(self, twitter_handle):
        self.twitter_handles = twitter_handles

    def soup(self, twitter_handle):
        """
        Send request to twitter for given username, runs the response through
        BeautifulSoup, and then stores the resulting data structure in 'soup'
        to be returned
        """
        source = requests.get(
            f"https://mobile.twitter.com/{twitter_handle}/with_replies"
        ).text
        # Use bs4 to handle the requests response.
        soup = BeautifulSoup(source, "lxml")
        return soup

    def store_tweet(self):
        """
        Sort through the returned information from 'soup' and then store it in
        a mongodb database.
        """
        for twitter_handle in self.twitter_handles:
            parse = self.soup(twitter_handle)
            profilePic = parse.find("td", class_="avatar").img["src"]
            tweet_lst = parse.find_all(
                "div", class_="tweet-text"
            )  # text of the tweet which we will have to extract with .text
            tweet_text_lst = [tweet.text for tweet in tweet_lst]
            tweet_id_lst = [tweet["data-id"] for tweet in tweet_lst]
            for i in range(len(tweet_lst)):
                # Format everything to be inserted into a collection
                entry = {
                    "handle": twitter_handle,
                    "tweet_id": tweet_id_lst[i],
                    "text": tweet_text_lst[i].strip(),
                    "link": f"https://mobile.twitter.com/{twitter_handle}/status/{tweet_id_lst[i]}",
                    "profilePic": profilePic,
                    "color": team_colors[twitter_handle],
                    "posted": False,
                }
                # Look for any matching ID's in that db so we don't enter in
                # something twice
                if posts.find_one({"tweet_id": tweet_id_lst[i]}):
                    pass
                else:
                    # Insert 'entry' into the db
                    posts.insert_one(entry).inserted_id

    def filterTweets(self):
        """
        Look through our aggregate(contains filtered tweets) for any
        documents, format them for discord, adn then send them in a
        discord webhook
        """
        lst = []
        empty = 0  # remains 0 if there are no entries for the aggregation
        webhook = webh(SET_SERVER)  # sets the server to post to
        for doc in posts.aggregate(pipeline):
            empty += 1
            # Extract the information from the db.
            lst.append([doc["handle"], doc["text"], doc["color"], doc["profilePic"]])
            # Update the db to show that we've posted this entry
            db.tweets.update_one({"_id": doc["_id"]}, {"$set": {"posted": True}})
        if empty > 0:
            # Format for embed
            data = twitter_webhook(lst)
            # Send message
            webhook.send(embeds=data)


def printParsedTweet():
    """
    This is main() for now, used to make and run our class
    and it's functions. It will be called from Discord_Bot.py
    but everyting will happen here.
    """
    user = TweetParser(twitter_handles)
    user.store_tweet()
    user.filterTweets()


# Select server to send messages in
def webh(serv):
    if SET_SERVER == "bl":
        webhook = Webhook.partial(
            bl_id_twitter, bl_token_twitter, adapter=RequestsWebhookAdapter()
        )
        return webhook
    else:
        webhook = Webhook.partial(
            dz_id_twitter, dz_token_twitter, adapter=RequestsWebhookAdapter()
        )
        return webhook


def setup(client):
    client.add_cog(Twitter(client))
