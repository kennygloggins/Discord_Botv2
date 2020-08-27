# By: Kenny_G_Loggins
# Created on: 8/4/20, 1:17 AM
# File: config_template.py
# Project: F1_discord_bot


# Your bot's Token
token = "put token here"  # can be found in your developer's portal where you created your bot

# Discord webhook credentials
webhook_id_reddit = ""
webhook_token_reddit = ""

webhook_id_twitter = ""
webhook_token_twitter = ""

# Channels to post in (depricated)
id_channel = "put number here"  # with discord in devmode(Settings/appearances) , right click channel to see copy id

# Subreddits to grab posts from. Make sure to put the list in [ str(sub name), int(upvotes needed)] format
# These values are used by reddit_bot.py as parameters for what posts to grab and print automatically in discord.
sublist = [["gifs", 8000], ["aww", 9000], ["HQG", 10000]]

# How often to query the subreddit for new post and post to id_channel:
reddit_frequency = 10  # in minutes
twitter_frequency = 1  # in minutes

# Number of tweets to pull and search through for each user
count = 10  # most recent posts

# Dictionary for twitter commands. (not implemented yet)
f1twit_dict = {
    "Merc": "https://twitter.com/MercedesAMGF1",
    "RBR": "https://twitter.com/redbullracing",
    "McL": "https://twitter.com/McLarenF1",
    "RP": "https://twitter.com/RacingPointF1",
    "AT": "https://twitter.com/AlphaTauriF1",
    "AR": "https://twitter.com/AlfaRomeoRacing",
    "Ren": "https://twitter.com/RenaultF1Team",
    "Hass": "https://twitter.com/HaasF1team",
    "Red": "https://twitter.com/scuderiaferrari",
    "WR": "https://twitter.com/WilliamsRacing",
    "Fdank": None,
    "WTF1": "https://twitter.com/wtf1official",
    "Fia": None,
    "F1": "https://twitter.com/F1",
}

# More things to search and respond to (not implemented yet)
addition_commands = {
    "Lewis": "Get in there Lewis!",
    "box": "box box, box, box.",
    "fiesta": "https://www.youtube.com/watch?v=3r2OkH7zU_c",
}

# Twitter handles to search for:
twitter_handles = [
    "MercedesAMGF1",
    "redbullracing",
    "McLarenF1",
    "RacingPointF1",
    "AlphaTauriF1",
    "AlfaRomeoRacing",
    "RenaultF1Team",
    "HaasF1team",
    "scuderiaferrari",
    "WilliamsRacing",
    "wtf1official",
    "F1",
    "KennyGLoggins",
]

# Keywords you want to look for in their tweets:
twitter_words = [
    "signed",
    "investigation",
    "out of the race",
    "will not start",
    "won't start",
]

# MongoDB server information. This is where the bots store the information they find. Without it they won't know
# if they've posted before or if there is important information in that media.
mongserver = "mongodb://user_name:pass@ip:27017/"

# Google calender ID to sync to F1 racing events. You can find the calender's id by clicking on the desired calender,
# going to settings, and scrolling down until you see 'Calender ID' with a string formatted like the one below.
googcal = "<big string of random characters here>@import.calendar.google.com"

# Twitter handles and their associated colors. These color codes tell discord what color to make the webhook sidebar.
team_colors = {
    "MercedesAMGF1": 53950,
    "redbullracing": 1982975,
    "McLarenF1": 16746240,
    "RacingPointF1": 16094920,
    "AlphaTauriF1": 16316664,
    "AlfaRomeoRacing": 10158080,
    "RenaultF1Team": 16774400,
    "HaasF1team": 7697781,
    "scuderiaferrari": 14417920,
    "WilliamsRacing": 1212635,
    "F1": 0,
    "KennyGLoggins": 1982975,
}

# A dictionary that associates F1 twitter handles with names associated with them. This is used to choose what color
# to post the reddit webhook in.
name_list = {
    "MercedesAMGF1": [
        "mercedesamgf1",
        "mercedes",
        "lewis",
        "hamilton",
        "valtteri",
        "bottas",
        "toto",
    ],
    "redbullracing": [
        "redbullracing",
        "red bull racing",
        "red bull",
        "max",
        "verstappen",
        "albon",
        "horner",
    ],
    "McLarenF1": [
        "mclarenF1",
        "mclaren",
        "zac brown",
        "lando",
        "norris",
        "sainz",
        "seidl",
    ],
    "RacingPointF1": [
        "racingpointf1",
        "racing point",
        "force india",
        "stroll",
        "perez",
        "tracingpoint",
    ],
    "AlphaTauriF1": ["alphataurif1", "gasly", "kvyat", "tauri"],
    "AlfaRomeoRacing": ["alfaromeoracing", "kimi", "raikkonen", "giovinazzi", "kubica"],
    "RenaultF1Team": ["renaultf1team", "ricciardo", "ocon", "cyril", "renault"],
    "scuderiaferrari": [
        "scuderiaferrari",
        "vettel",
        "leclerc",
        "binotto",
        "ferrari",
        "red haas",
        "seb",
    ],
    "HaasF1team": ["haasf1team", "magnussen", "grosjean", "steiner", "haas"],
    "WilliamsRacing": [
        "williamsracing",
        "claire",
        "williams",
        "russell",
        "latifi",
        "chadwick",
    ],
    "F1": ["croft", "brundle", "fia", "kravitz", "rosberg", "button"],
}
