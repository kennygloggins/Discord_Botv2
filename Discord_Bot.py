# By: Kenny_G_Loggins
# Created on: 8/27/20, 2:43 AM
# File: Discord_Bot.py
# Project: F1 Discord Bot


import discord
from discord.ext import commands
from discord import Webhook, RequestsWebhookAdapter
import asyncio

# Check config.py and change these values
from config import (
    token,
    id_channel,
    webhook_id_reddit,
    webhook_token_reddit,
)


client = commands.Bot(command_prefix=".")

# Print's the bot's information to console when on and ready.
@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")


@client.command()
async def load(ctx, extension):
    client.load_extension(f"cog.{extension}")
    print(f"{extension} cog loaded.")
    await ctx.send(f"```{extension} cog loaded.```")


@client.command()
async def unload(ctx, extension):
    client.unload_extension(f"cog.{extension}")
    print(f"{extension} cog unloaded.")
    await ctx.send(f"```{extension} cog unloaded.```")


# Start client
client.load_extension("cog.twitter")
client.run(str(token))
