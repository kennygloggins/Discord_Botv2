from bs4 import BeautifulSoup
from cog.webhook import twitter_webhook, convo_webhook
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
convo = db.convo

# Filter for our aggregation
pipelineP = [{"$match": {"text": {"$regex": twitter_words}, "posted": False}}]
pipelineC = [
    {"$match": {
        "$expr": {"$ne": ["$main.handle", "$reply.handle"]}, "posted": False}}
]

# Variable for server to post in
webhook = Webhook.partial(
    bl_id_twitter, bl_token_twitter, adapter=RequestsWebhookAdapter()
)
# webhook = Webhook.partial(
#     dz_id_twitter, dz_token_twitter, adapter=RequestsWebhookAdapter()
# )


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

        if soup.find("div", class_="tweet-reply-context"):
            self.extract_replies(soup, twitter_handle)
        return soup

    def soup_convo(self, soup, tweet_id, twitter_handle):
        """
        Use this when a reply is found. It runs BeautifulSoup() on the
        coversation.
        """

        source = requests.get(
            f"https://mobile.twitter.com/{twitter_handle}/status/{tweet_id}"
        ).text
        soup = BeautifulSoup(source, "lxml")
        self.twitter_convo(soup)

    def store_tweet(self):
        """
        Sort through the returned information from 'soup' and then store it in
        a mongodb database.
        """

        for twitter_handle in self.twitter_handles:
            parse = self.soup(twitter_handle)
            profilePic = parse.find("td", class_="avatar").img["src"]
            # text of the tweet which we will have to extract with .text
            tweet_lst = parse.find_all("div", class_="tweet-text")
            tweet_text_lst = [tweet.text for tweet in tweet_lst]
            tweet_id_lst = [tweet["data-id"] for tweet in tweet_lst]

            for i in range(len(tweet_lst)):
                # Format into json for mongoDB
                entry = {
                    "handle": twitter_handle,
                    "tweet_id": tweet_id_lst[i],
                    "text": tweet_text_lst[i].strip(),
                    "link": f"https://mobile.twitter.com/{twitter_handle}/status/{tweet_id_lst[i]}",
                    "profilePic": profilePic,
                    "color": team_colors[twitter_handle.lower()],
                    "posted": False,
                }
                # Insert collection into the db
                posts.insert_one(entry).inserted_id

    def filterTweets(self):
        """
        Look through our aggregate(contains filtered tweets) for any
        documents, format them for discord, adn then send them in a
        discord webhook
        """

        lst = []
        empty = 0  # remains 0 if there are no entries for the aggregation

        for doc in posts.aggregate(pipelineP):
            empty += 1
            # Extract the information from the db.
            lst.append([doc["handle"], doc["text"],
                        doc["color"], doc["profilePic"]])
            # Update the db to show that we've posted this entry
            db.tweets.update_one({"_id": doc["_id"]}, {
                                 "$set": {"posted": True}})

        if empty > 0:
            # Format for embed
            data = twitter_webhook(lst)
            # Send message
            webhook.send(embeds=data)

    def extract_replies(self, soup, twitter_handle):
        reply_tweet_id = []
        reply_to = []
        tweet_lst = soup.find_all("tr", class_="tweet-container")

        for tweet in tweet_lst:
            if tweet.find("div", class_="tweet-reply-context"):
                reply_tweet_id.append(tweet.find(
                    "div", class_="tweet-text")["data-id"])
                reply_to.append(
                    tweet.find("div", class_="tweet-reply-context").a["href"]
                )

        interested_tweets = [
            {"tweet_id": tweet_id, "handle": thandle[1:]}
            for i in twitter_handles
            for tweet_id, thandle in zip(reply_tweet_id, reply_to)
            if thandle[1:] == i
        ]

        for handle_id in interested_tweets:
            if len(handle_id) > 0:
                self.soup_convo(
                    soup, handle_id["tweet_id"], handle_id["handle"])

    def twitter_convo(self, soup):
        """
        Extra all the information from a conversation, format it to a document,
        check if document exist in db, and then if it doesn't, store that
        document in the mongodb.
        """

        # Grab variables for main tweet in convo
        main = soup.find("div", {"class": "timeline inreplytos"})
        main_handle = main.find("a")["href"][1:-4]
        main_avatar = main.find("img")["src"]  # Profile pic for main tweet
        main_id = main.find("div", {"class": "tweet-text"})["data-id"]
        main_text = main.find(
            "div", {"class": "tweet-text"}).get_text(strip=True)

        # Grab variables for reply tweet in convo
        reply_tweet = soup.find("div", {"class": "tweet-detail"})
        reply_handle = reply_tweet.find("a")["href"][1:-4]
        reply_avatar = reply_tweet.find("td").img["src"]
        reply_id = reply_tweet.find("div", {"class": "tweet-text"})["data-id"]
        reply_text = reply_tweet.find("div", {"class": "tweet-text"}).get_text(
            strip=True
        )
        try:
            main_color = team_colors[main_handle.lower()]
        except KeyError:
            main_color = None
        try:
            reply_color = team_colors[reply_handle.lower()]
        except KeyError:
            reply_color = None

        # Format into json for mongoDB
        entry = {
            "main": {
                "handle": main_handle,
                "avatar": main_avatar,
                "color": main_color,
                "tweet_id": main_id,
                "text": main_text,
                "link": f"https://mobile.twitter.com/{main_handle}/status/{main_id}",
            },
            "reply": {
                "handle": reply_handle,
                "avatar": reply_avatar,
                "color": reply_color,
                "tweet_id": reply_id,
                "text": reply_text,
                "link": f"https://mobile.twitter.com/{reply_handle}/status/{reply_id}",
            },
            "posted": False,
        }
        # Insert collection into the db
        convo.insert_one(entry).inserted_id

    def filterConvo(self):
        content = "➖➖➖➖➖➖➖➖➖➖➖➖"

        for doc in convo.aggregate(pipelineC):
            print(doc)
            # Extract the information from the db.
            main_lst = [
                doc["main"]["handle"],
                doc["main"]["text"],
                doc["main"]["color"],
                doc["main"]["avatar"],
                doc["main"]["link"],
            ]
            reply_lst = [
                doc["reply"]["handle"],
                doc["reply"]["text"],
                doc["reply"]["color"],
                doc["reply"]["avatar"],
                doc["reply"]["link"],
            ]
            # Update the db to show that we've posted this entry
            db.convo.update_one({"_id": doc["_id"]}, {
                                "$set": {"posted": True}})
            # Format for embed
            data = convo_webhook(main_lst, reply_lst)
            # Send message
            webhook.send(content=content, embeds=data)


def printParsedTweet():
    """
    This is main() for now, used to make and run our class
    and it's functions. It will be called from Discord_Bot.py
    but everyting will happen here.
    """

    user = TweetParser(twitter_handles)
    user.store_tweet()
    user.filterTweets()
    user.filterConvo()


def setup(client):
    client.add_cog(Twitter(client))
