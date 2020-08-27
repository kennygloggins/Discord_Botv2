from bs4 import BeautifulSoup
import requests
from config import *
import re
from pymongo import MongoClient
import discord
from discord.ext import commands
from cog.webhook import twitter_webhook

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

class Twitter(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Twitter extension loaded.')

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")

def setup(client):
    client.add_cog(Twitter(client))
    
class TweetParser():
    """Take a tweet's information and rebundle it for use in a webhook.
    The plan is to recreate a conversation when there is one and also
    search for keywords.
    """
    def __init__(self, twitter_handle, key_words, team_colors):
        self.twitter_handle = twitter_handle
        self.key_words = key_words
        self.team_colors = team_colors

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

    def parse(self, soup, handle):
        """Centeralised function for calling individual functions to parse twitter
        for given usernames.

        Args:
            soup (data structure): what's returned from BeautifulSoup()
            handle (str): Twitter username

        Returns:
            dictionary: contains filtered tweets and profile picture links values for
            twitter handle keys.
        """
        tweets = {}
        profilePic = soup.find("td", class_="avatar").img["src"]
        tweet_texts, tweet_ids = self.tweet(soup)
        filteredTweets = self.filterTweets(tweet_texts)
        # repliesToR = self.conversation(soup)
        tweets[handle] = {"filteredTweets": filteredTweets, "profilePic": profilePic}
        return tweets  # , repliesToR

    def tweet(self, soup):
        """Returns a dictionary with tweet id's as keys and their text as values"""
        tweet_dic = {}
        tweet_lst = soup.find_all(
            "div", class_="tweet-text"
        )  # text of the tweet which we will have to extract with .text
        tweet_ids = soup.find("div", class_="tweet-text")
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
        filteredTweets = {}
        for tweet in tweet_texts:
            for word in self.key_words:
                if re.search(word, tweet_texts[tweet]):
                    filteredTweets[tweet] = tweet_texts[tweet]
        if len(filteredTweets) == 0:
            return None
        else:
            return filteredTweets

    def printParsedTweet(self):
        """This is main() for now, used to make and run our class
        and it's functions. It will be called from Discord_Bot.py
        but everyting will happen here.
        """
        for handle in self.twitter_handles:
            conversation = {}
            name = handle
            filteredTweets, profilePic, repliesTo = self.parse(
                handle, self.key_words
            )
            conversation[handle] = [filteredTweets, profilePic, repliesTo]
        return conversation




# data = twitter_webhook(twitHandle, tweets[twitHandle]["filteredTweets"], team_colors[twitHandle], tweets[twitHandle]["profilePic"])  # , tweet_id
# webhook.send(embeds=data)
