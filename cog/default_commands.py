from config import webhook_id_twitter, webhook_token_twitter, f1twit_lst
from discord import Webhook, RequestsWebhookAdapter
from discord.ext import commands

webhook = Webhook.partial(
    webhook_id_twitter, webhook_token_twitter, adapter=RequestsWebhookAdapter()
)


class DefaultCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.bgtask.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Default Commands extension loaded.")

    @commands.command()
    async def f1twitter(self, ctx):
        await ctx.send(f1twit_lst)


def setup(client):
    client.add_cog(DefaultCommands(client))
