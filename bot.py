from datetime import datetime
import os
import time
import discord
import asyncio
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle
from dotenv import load_dotenv
from functions import *
from collections import OrderedDict
from embeds import helpList

# ----------yt stuff----------

from google_auth_oauthlib.flow import Flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]



def main():
    load_dotenv()
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix='qr ',intents=intents,status=discord.Status.dnd,activity=discord.Game("with my source code 😳"), help_command=None)
    
    DiscordComponents(bot)

    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')

    @bot.event
    async def on_ready():
        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('------')
        print(os.path.expanduser("~"))
    bot.launch_time=datetime.utcnow()

    @bot.command(name='uptime')
    async def uptime(ctx):
        delta_uptime=datetime.utcnow()-bot.launch_time
        h,r=divmod(delta_uptime.total_seconds(),3600)
        m,s=divmod(r,60)
        d,h=divmod(h,24)
        await ctx.reply(f'{int(d)}days, {int(h)} hours, {int(m)} minutes, {int(s)} seconds have elapsed since starting the bot.')

    @bot.command(name='save')
    async def save(ctx, messageSong=None):
        user = ctx.message.author
        try:
            if messageSong == None:
                message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                if ctx.message.reference.resolved.author.display_name == "Hydra":  # hydra
                    songLink = message.embeds[0].url

                else:
                    songLink = message.embeds[0].description
                    songLink = songLink.split("https")[1]
                    songLink = songLink.split(")")[0]
                    songLink = "https" + songLink
                await user.send(songLink)

            else:
                await user.send(messageSong)
            await ctx.message.add_reaction("👌")

        except discord.errors.Forbidden:  # check if DM Closed

            embed = discord.Embed(
                title="UH OH!", description="Looks like I'm unable to send you a Direct Message :(", color=0xFF0000)
            embed.add_field(
                name="NOTE", value="**Make sure this is turned on so that the bot is able to DM you!**", inline=True)
            embed.set_image(
                url="https://support.discord.com/hc/article_attachments/360062973031/Screen_Shot_2020-07-24_at_10.46.47_AM.png")
            embed.set_footer(text="Embed Support for Discord errors")
            await ctx.send(user.mention, embed=embed)

    @bot.command(name="help")
    async def support(ctx):
        # Set a default embed first
        current = 0
        mainMessage = await ctx.reply(
            "**Support has arrived!**",
            embed=helpList[current],
            components=[
                [
                    Button(
                        label="Prev",
                        id="back",
                        style=ButtonStyle.blue
                    ),
                    Button(
                        label=f"Page {int(helpList.index(helpList[current])) + 1}/{len(helpList)}",
                        id="cur",
                        style=ButtonStyle.grey,
                        disabled=True
                    ),
                    Button(
                        label="Next",
                        id="front",
                        style=ButtonStyle.blue
                    )
                ]
            ]
        )

        while True:
            # Try and except blocks to catch timeout and break
            try:
                interaction = await bot.wait_for(
                    "button_click",
                    check=lambda i: i.component.id in ["back", "front"],
                    timeout=60  # 60 seconds of inactivity
                )
                # Getting the right list index
                if interaction.component.id == "back":
                    current -= 1
                elif interaction.component.id == "front":
                    current += 1
                # If its out of index, go back to start / end
                if current == len(helpList):
                    current = 0
                elif current < 0:
                    current = len(helpList) - 1

                # Edit to new page + the center counter
                await interaction.respond(
                    type=7,
                    embed=helpList[current],
                    components=[
                        [
                            Button(
                                label="Prev",
                                id="back",
                                style=ButtonStyle.blue
                            ),
                            Button(
                                label=f"Page {int(helpList.index(helpList[current])) + 1}/{len(helpList)}",
                                id="cur",
                                style=ButtonStyle.grey,
                                disabled=True
                            ),
                            Button(
                                label="Next",
                                id="front",
                                style=ButtonStyle.blue
                            )
                        ]
                    ]
                )
            except asyncio.TimeoutError:
                # Disable and get outta here
                await mainMessage.edit("*This interaction has expired now*",
                                       components=[
                                           [
                                               Button(
                                                   label="Prev",
                                                   id="back",
                                                   style=ButtonStyle.blue,
                                                   disabled=True
                                               ),
                                               Button(
                                                   label=f"Page {int(helpList.index(helpList[current])) + 1}/{len(helpList)}",
                                                   id="cur",
                                                   style=ButtonStyle.grey,
                                                   disabled=True
                                               ),
                                               Button(
                                                   label="Next",
                                                   id="front",
                                                   style=ButtonStyle.blue,
                                                   disabled=True
                                               )
                                           ]
                                       ]
                                       )
                break

    # very bad implementaion, code just works tho
    @bot.command(name='fetch')
    async def fetch(ctx):
        listOfAllTracks = ["sample"]
        currentPgQueueMessage = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        # getting the last message ("qr fetch")
        lastMessage = ctx.message
        # user who invoked the command
        userName = lastMessage.author
        # server on which the command was invoked
        guildName = lastMessage.guild
        # ID of the queue message
        queueMessageID = currentPgQueueMessage.id

        pageNumber = 1
        while True:
            cancelMessage = await ctx.channel.history(limit=1).flatten()
            if cancelMessage[0].content == "cancel":
                await ctx.send("Cancelling request")
                return 0
            time.sleep(0.5)
            currentPgQueueMessage = await ctx.fetch_message(queueMessageID)
            # fetch msg
            currentPgQueueMessageContent = currentPgQueueMessage.content
            # print(currentPgQueueMessageContent)
            currentPgListOfAllTracks = currentPgQueueMessageContent.split("\n")
            # print(currentPgListOfAllTracks)
            currentPgListOfAllTracks.pop()              # removing the last element ("```")
            # removing the first element ("```nim")
            currentPgListOfAllTracks.pop(0)
            # Important as we check if we have reached the end or not
            lastSentence = currentPgListOfAllTracks[-1].strip()
            # removing the last element
            currentPgListOfAllTracks.pop()
            # this variable is to get rid of the "left" thing
            itemIndexWhereLeftIs = None
            for item in currentPgListOfAllTracks:
                if "current track" in item:
                    currentPgListOfAllTracks.remove(item)
            for item in currentPgListOfAllTracks:
                strippedItem = item.strip()
                if strippedItem[-4:] == "left":
                    itemIndexWhereLeftIs = currentPgListOfAllTracks.index(item)

            if type(itemIndexWhereLeftIs) == int:
                currentPgListOfAllTracks[itemIndexWhereLeftIs] = currentPgListOfAllTracks[itemIndexWhereLeftIs].strip(
                ).rstrip("left")  # removing the "left"
            formattedMessage = "\n".join(currentPgListOfAllTracks).strip()

            # if the current message is same as last, we dont add this in the queuepages
            if formattedMessage == listOfAllTracks[-1]:
                continue
            else:
                # See if this page is the last page, if yes, break

                listOfAllTracks.append(formattedMessage)
                await ctx.send(pageNumber)
                pageNumber += 1
                if lastSentence == "This is the end of the queue!":
                    c = "All " + str(pageNumber) + " pages have been fetched!"
                    await ctx.send(c)
                    break
        # getting rid of that "sample"
        listOfAllTracks.pop(0)

        # As of now, the listOfAllTracks is a list of "blocks" of tracks, rather than actual tracks, has inconsistent whitespaces,  and may have some duplicates

        # Flattening the list out and removing whitespaces:
        newListOfAllTracks = []
        for block in listOfAllTracks:
            tracks = block.split("\n")
            for track in tracks:
                newListOfAllTracks.append(track.strip())

        listOfAllTracks = newListOfAllTracks
        del newListOfAllTracks

        # Removing duplicates
        listOfAllTracks = OrderedDict.fromkeys(listOfAllTracks)
        listOfAllTracks = list(listOfAllTracks)

        # printing to console the final parsed currentPgListOfAllTracks.
        queueFileName = "queueFile_" + str(userName) + str(guildName) + ".txt"
        queueFile = open(queueFileName, "w")
        for item in listOfAllTracks:
            queueFile.write(item)
            queueFile.write("\n")
        queueFile.close()
        await ctx.send(file=discord.File(queueFileName))
        os.remove(queueFileName)

    @bot.command(name='makepl')
    async def makepl(ctx, playlistName):
        queueFile = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        textFileAttachment = queueFile.attachments[0]
        messageFile = await textFileAttachment.read()
        messageContent = messageFile.decode("utf-8").strip()
        user = ctx.author

        listOfListOfTrackInfo = splitQueueFile(messageContent)

        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "google-credentials.json"

        # Get credentials and create an API client

        flow = Flow.from_client_secrets_file(
            client_secrets_file, scopes, redirect_uri='urn:ietf:wg:oauth:2.0:oob')

        auth_url = flow.authorization_url()

        stringo = auth_url[0]
        embed = discord.Embed(title="OAuth Verification Embed",
                              description="Please go to the following URL:", color=0x34A853)
        embed.add_field(name="OAuth Link",
                        value="[Click Here]({})".format(stringo))
        embed.add_field(
            name="Instructions", value="Sign-In to your Google Account and paste the token here (obtained after authorising the bot to modify your Youtube data)")
        embed.add_field(name="Made a mistake?",
                        value="Type `cancel` to invalidate the OAuth process.")
        embed.set_footer(text="OAuth Embed generated for {}".format(user))

        try:
            await user.send(embed=embed)
            await ctx.send("{} check your DMs!".format(user.mention))

            def check(mssg):
                return mssg.author == ctx.message.author

            while True:
                msg = await bot.wait_for("message", check=check)
                if 'cancel' in msg.content.lower():
                    await user.send("Cancelling request")
                    return 0
                time.sleep(0.5)
                codeMessage = msg.content
                break

        except discord.errors.Forbidden:  # check if DM Closed
            embed = discord.Embed(
                title="UH OH!", description="Looks like I'm unable to send you a Direct Message :(", color=0xFF0000)
            embed.add_field(
                name="NOTE", value="**Make sure this is turned on so that the bot is able to DM you!**", inline=True)
            embed.set_image(
                url="https://support.discord.com/hc/article_attachments/360062973031/Screen_Shot_2020-07-24_at_10.46.47_AM.png")
            embed.set_footer(text="Embed Support for Discord errors")
            await ctx.send(user.mention, embed=embed)

        async with ctx.typing():

            flow.fetch_token(code=codeMessage)
            credentials = flow.credentials

            youtube = googleapiclient.discovery.build(
                api_service_name, api_version, credentials=credentials)

            # ============= Making the playlist =============
            request = youtube.playlists().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": playlistName,
                        "description": "This is a playlist created by Q-Loggr. Star: https://github.com/StaticESC/Q-Loggr-Bot. Thank you.",
                        "tags": [
                            "sample playlist",
                            "API call"
                        ],
                        "defaultLanguage": "en"
                    },
                    "status": {
                        "privacyStatus": "public"
                    }
                }
            )
            response = request.execute()

            playlistID = response.get('id')

            # ======== Searching and adding the songs to the playlist =========

            # Reversing the list cuz yt displays videos in "date added (newest)" form
            for listOfTrackinfo in listOfListOfTrackInfo[::-1]:

                # ======== Searching ========
                songNameAndArtist = listOfTrackinfo[1]

                request = youtube.search().list(
                    part="snippet",
                    maxResults=1,
                    q=songNameAndArtist
                )

                response = request.execute()
                videoID = response.get('items')[0].get('id').get('videoId')

                # ======== Adding to playlist ========
                request = youtube.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlistID,
                            "position": 0,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": videoID
                            }
                        }
                    }
                )

                response = request.execute()
                playlistURL = "https://www.youtube.com/playlist?list=" + playlistID

                message = "The playlist URL is: " + playlistURL

        await ctx.send(message)
    bot.run(DISCORD_TOKEN)


if __name__ == '__main__':
    main()
