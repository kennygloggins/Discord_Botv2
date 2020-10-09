from discord import Embed, Color
from config import team_colors
import re


# def reddit_webhook(title, post, name):

#     img = [".jpeg", ".png", ".gif", ".bmp", ".jpg"]
#     video = ["youtube", ".mp4", ".mov", ""]

#     try:
#         color = team_colors[name]
#     except KeyError:
#         color = 0

#     for ftype in img:
#         if re.search(ftype, post):
#             data = Embed(title=title, color=Color(
#                 color), url=post).set_image(url=post)
#             return data

#     # for ftype in video

#     data = Embed(title=title, color=Color(color), url=post)
#     return data


def reddit_webhook(lst):

    img = [".jpeg", ".png", ".gif", ".bmp", ".jpg"]
    data = []
    for item in lst:
        for ftype in img:
            if re.search(ftype, item[1]):
                data.append(Embed(title=item[0], color=Color(item[2]), url=item[1]).set_image(url=item[1]))
            else:
                data.append(Embed(title=item[0], color=Color(item[2]), url=item[1]))
    return data


def twitter_webhook(lst):

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


def convo_webhook(main, reply):

    data = [
        Embed(description=main[1], color=Color(main[2])).set_author(
            name=f"@{main[0]}", url=main[4], icon_url=main[3],
        ),
        Embed(description=reply[1], color=Color(reply[2])).set_author(
            name=f"@{reply[0]}", url=reply[4], icon_url=reply[3],
        ),
    ]
    return data
