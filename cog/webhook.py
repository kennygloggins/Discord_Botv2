from discord import Webhook, RequestsWebhookAdapter, Embed, Color
from config import webhook_id_reddit, webhook_token_reddit, team_colors
import re
import discord


def reddit_webhook(title, post, name):
    img = [".jpeg", ".png", ".gif", ".bmp"]
    try:
        color = team_colors[name]
    except KeyError:
        color = 0
    for x in img:
        if re.search(x, post):
            data = Embed(title=title, color=Color(color), url=post).set_image(url=post)
            return data

    data = Embed(title=title, color=Color(color), url=post)
    return data


"""def twitter_webhook(handle, tweet, color, profilePic):
    data = Embed(description=tweet, color=Color(color)).set_author(
        name="@KennyGLoggins",
        url="https://mobile.twitter.com/KennyGLoggins",
        icon_url="https://pbs.twimg.com/profile_images/567516929/Kenny_Powers_x96.jpg",
    )
    return data"""


def twitter_webhook(handle, tweets, color, profilePic): # , tweet_id
    data = []
    for tweet in tweets:
        data.append(
            Embed(description=tweet, color=Color(color)).set_author(
                name=f"@{handle}",
                url=f"https://mobile.twitter.com/{handle}",
                icon_url=profilePic,
            )
        )
    return data


"""class Webhook:

    def __init__(self, authors_name, authors_url, authors_pic, footer, color, media):
        self.authors_name = authors_name
        self.authors_url = authors_url
        self.authors_pic = authors_pic
        self.footer = footer
        self.color = color
        self.media = media

    def embed(self):
        embed = Embed(color=self.color, desc)"""

