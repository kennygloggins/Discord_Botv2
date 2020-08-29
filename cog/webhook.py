from discord import Embed, Color
from config import team_colors
import re


def reddit_webhook(title, post, name):
    img = [".jpeg", ".png", ".gif", ".bmp", ".jpg"]
    video = ["youtube", ".mp4", ".mov", ""]
    try:
        color = team_colors[name]
    except KeyError:
        color = 0
    for ftype in img:
        if re.search(ftype, post):
            data = Embed(title=title, color=Color(color), url=post).set_image(url=post)
            return data
    
    #for ftype in video

    data = Embed(title=title, color=Color(color), url=post)
    return data


"""def twitter_webhook(handle, tweet, color, profilePic):
    data = Embed(description=tweet, color=Color(color)).set_author(
        name="@KennyGLoggins",
        url="https://mobile.twitter.com/KennyGLoggins",
        icon_url="https://pbs.twimg.com/profile_images/567516929/Kenny_Powers_x96.jpg",
    )
    return data"""


def twitter_webhook(lst):  # , tweet_id
    data = []
    for item in lst:
        data.append(
            Embed(description=item[1], color=Color(item[2])).set_author(
                name=f"@{item[0]}",
                url=f"https://mobile.twitter.com/{item[0]}",
                icon_url=item[3],
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
