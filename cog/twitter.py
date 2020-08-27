from bs4 import BeautifulSoup
from cog.webhook import twitter_webhook
from config import *
import discord
from discord import Webhook, RequestsWebhookAdapter
from discord.ext import commands, tasks
import requests
import re
from pymongo import MongoClient


"""
source = requests.get(f'https://mobile.twitter.com/HaasF1Team/with_replies').text
soup = BeautifulSoup(source, 'lxml')
spans = soup.find("div", class_="tweet-reply-context username").a['href']
print(spans)
"""

# Setup connection to mongodb collection
server = MongoClient(mongserver)
db = server.twitter_db
posts = db.reddit_test

webhook = Webhook.partial(
    webhook_id_twitter, webhook_token_twitter, adapter=RequestsWebhookAdapter()
)


class Twitter(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.bgtask.start()

    def cog_unload(self):
        self.bgtask.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Twitter extension loaded.")

    @tasks.loop(minutes=twitter_frequency)
    async def bgtask(self):
        printParsedTweet()

    @bgtask.before_loop
    async def before_task(self):
        print("waiting...")
        await self.client.wait_until_ready()


class TweetParser:
    """Take a tweet's information and rebundle it for use in a webhook.
    The plan is to recreate a conversation when there is one and also
    search for keywords.
    """

    def __init__(self, twitter_handle):
        self.twitter_handle = twitter_handle

    def soup(self):
        """Send request to twitter for each username, run response through 
        BeautifulSoup, and then store the results data structure in 'soup' 
        to be returned"""
        source = requests.get(
            f"https://mobile.twitter.com/{self.twitter_handle}/with_replies"
        ).text
        # Use bs4 to handle the requests response.
        soup = BeautifulSoup(source, "lxml")
        return soup

    def conversation(self, soup):
        """Stitch together replies, handles, and profile pictures
        to look like a conversation in a discord webhook"""
        repliesToR = []
        # grabs tweet id as a string, can be used to look up full conversations
        tweet_id = soup.find("div", class_="tweet-text")["data-id"]
        repliesToLst = soup.find_all("div", class_="tweet-reply-context username")
        for repliesTo in repliesToLst:
            repliesToR.append(repliesTo.a["href"])
        if repliesTo:
            for reply in repliesTo:
                reply = reply.strip("/")
                # TODO finish filtering reply list and add it to a dictionary

    def tweet(self, soup):
        """Returns a dictionary with tweet id's as keys and their text as values"""
        tweet_lst = soup.find_all(
            "div", class_="tweet-text"
        )  # text of the tweet which we will have to extract with .text
        tweet_text_lst = [tweet.text for tweet in tweet_lst]
        tweet_id_lst = [tweet["data-id"] for tweet in tweet_lst]
        tweet_id_text = {
            tweet_id: tweet_text.strip()
            for tweet_id, tweet_text in zip(tweet_id_lst, tweet_text_lst)
        }  # clean up tweet text and associate it with it's id in a dictionary
        return tweet_id_text

    def filterTweets(self, tweet_texts):
        """Look through tweet texts for keywords and return a 
        list of tweets that contain the words. Also grab just
        the strings out of the div's. Returns a list of strings"""
        filtered_tweet = []
        for tweet_id in tweet_texts:
            for word in twitter_words:
                if re.search(word, tweet_texts[tweet_id]):
                    filtered_tweet.append(tweet_texts[tweet_id])
        if len(filtered_tweet) == 0:
            return None
        else:
            return filtered_tweet


def printParsedTweet():
    """This is main() for now, used to make and run our class
    and it's functions. It will be called from Discord_Bot.py
    but everyting will happen here.
    """
    for handle in twitter_handles:
        user = TweetParser(handle)
        soup = user.soup()
        profilePic = soup.find("td", class_="avatar").img["src"]
        tweets = user.tweet(soup)
        filteredTweets = user.filterTweets(tweets)
        if filteredTweets == None:
            continue
        else:
            data = twitter_webhook(
                handle, filteredTweets, team_colors[handle], profilePic,
            )
            try:
                webhook.send(embeds=data)
            except InvalidArgument:
                webhook.send(
                    content="Too many results, please add more filters in config."
                )


def setup(client):
    client.add_cog(Twitter(client))
