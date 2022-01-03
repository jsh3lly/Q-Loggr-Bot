import discord
from discord.ext import commands
import ipinfo
import os
from dotenv import load_dotenv

load_dotenv()
IPINFO_TOKEN = os.getenv('IPINFO_TOKEN')


class Utils(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name='where', aliases=['info', 'server', 'details'])
    async def where(self, ctx):
        access_token = os.getenv('IPINFO_TOKEN')
        handler = ipinfo.getHandler(access_token)
        details = handler.getDetails()

        embed = discord.Embed(title="Server and Region Details for Q-Loggr",
                              description="Know where the bot is hosted currently.", color=0x88EAFF)
        embed.add_field(name="Organisation Name", value=details.org)
        try:
            embed.add_field(name="Host", value=details.hostname)
        except AttributeError:
            embed.add_field(name="Host", value="localhost")
        embed.add_field(name="City", value=details.city)
        embed.add_field(name="Country", value=details.country_name)
        embed.set_footer(text="Q-Loggr Utility")
        await ctx.send(embed=embed)

    @commands.command(name='ping', aliases=['pong'])
    async def ping(self, ctx):
        await ctx.reply(f'Pong! The ping is {round(self.client.latency * 1000)} ms.')


def setup(client):
    client.add_cog(Utils(client))
